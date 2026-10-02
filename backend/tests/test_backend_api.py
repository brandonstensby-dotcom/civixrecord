"""
CivixRecord-OS Backend API Hermetic Test Suite
Comprehensive tests verifying all REST endpoints, WebSockets, WebRTC signaling,
bylaws, metrics, and background transcription workers.
"""

import asyncio
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app, transcription_worker
from backend.app.services.transcription_worker import AudioJob, TranscriptionWorker, STTEngine
from civixrecord.analysis.motion_extractor import MotionExtractor


@pytest.fixture(scope="module")
def client():
    """Hermetic TestClient fixture exercising the full FastAPI application."""
    with TestClient(app) as test_client:
        yield test_client


# ============================================================================
# 1. Observability, Healthz & Prometheus Metrics Tests
# ============================================================================

def test_healthz_endpoint(client: TestClient):
    """Verifies the /healthz liveness probe."""
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "project" in data


def test_readyz_endpoint(client: TestClient):
    """Verifies the /readyz readiness probe."""
    response = client.get("/readyz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["worker_running"] is True


def test_prometheus_metrics_endpoint(client: TestClient):
    """Verifies Prometheus metrics output endpoint format."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    metrics_text = response.text
    assert "civix_http_requests_total" in metrics_text
    assert "civix_audio_chunks_processed_total" in metrics_text


# ============================================================================
# 2. Meeting Lifecycle Management Tests (/api/v1/meetings)
# ============================================================================

def test_create_and_get_meeting(client: TestClient):
    """Tests creating a meeting, fetching it by ID, and listing all meetings."""
    # 1. Create meeting
    payload = {
        "title": "Town of High River Regular Council Meeting",
        "municipality": "High River",
        "platform": "zoom",
        "meeting_url": "https://zoom.us/j/123456789",
    }
    create_res = client.post("/api/v1/meetings/", json=payload)
    assert create_res.status_code == 201
    meeting = create_res.json()
    meeting_id = meeting["meeting_id"]
    assert meeting["title"] == payload["title"]
    assert meeting["municipality"] == payload["municipality"]
    assert meeting["platform"] == "zoom"
    assert meeting["is_active"] is True
    assert meeting["in_camera_locked"] is False

    # 2. Get meeting by ID
    get_res = client.get(f"/api/v1/meetings/{meeting_id}")
    assert get_res.status_code == 200
    assert get_res.json()["meeting_id"] == meeting_id

    # 3. List all meetings
    list_res = client.get("/api/v1/meetings/")
    assert list_res.status_code == 200
    meeting_list = list_res.json()
    assert any(m["meeting_id"] == meeting_id for m in meeting_list)

    # 4. Non-existent meeting
    not_found_res = client.get("/api/v1/meetings/mtg-nonexistent999")
    assert not_found_res.status_code == 404


def test_in_camera_toggle(client: TestClient):
    """Tests statutory in-camera privacy lock toggle."""
    # Create meeting
    create_res = client.post("/api/v1/meetings/", json={
        "title": "Confidential Land Committee Meeting",
        "municipality": "Calgary",
        "platform": "webrtc",
    })
    meeting_id = create_res.json()["meeting_id"]

    # Lock in-camera
    lock_res = client.post(f"/api/v1/meetings/{meeting_id}/in-camera-lock?locked=true")
    assert lock_res.status_code == 200
    assert lock_res.json()["statutory_fence"] == "MUTED_IN_CAMERA_SESSION"

    # Verify state updated in GET
    get_res = client.get(f"/api/v1/meetings/{meeting_id}")
    assert get_res.json()["in_camera_locked"] is True

    # Unlock out of in-camera
    unlock_res = client.post(f"/api/v1/meetings/{meeting_id}/in-camera-lock?locked=false")
    assert unlock_res.status_code == 200
    assert unlock_res.json()["statutory_fence"] == "UNMUTED_PUBLIC_SESSION"


# ============================================================================
# 3. Motion Parsing & Procedural Flowchart Tests (/api/v1/motions)
# ============================================================================

def test_parse_motions_from_transcript(client: TestClient):
    """Tests extracting formal motions, movers, seconders, and outcomes."""
    utterances = [
        {
            "speaker": "Mayor Snodgrass",
            "text": "We will now consider the downtown revitalisation grant.",
            "timestamp": 12.0,
            "confidence": 0.98,
        },
        {
            "speaker": "Councillor Jones",
            "text": "I move that council approve the downtown grant as presented.",
            "timestamp": 15.5,
            "confidence": 0.99,
        },
        {
            "speaker": "Councillor Smith",
            "text": "Seconded by Councillor Smith.",
            "timestamp": 18.2,
            "confidence": 0.95,
        },
        {
            "speaker": "Mayor Snodgrass",
            "text": "All in favour? Opposed? The motion is carried unanimously.",
            "timestamp": 25.0,
            "confidence": 0.97,
        },
    ]

    response = client.post("/api/v1/motions/parse", json=utterances)
    assert response.status_code == 200
    motions = response.json()
    assert len(motions) >= 1
    motion = motions[0]
    assert motion["mover"] == "Councillor Jones"
    assert "approve the downtown grant" in motion["motion_text"]
    assert motion["seconder"] == "Councillor Smith"
    assert motion["outcome"] == "CARRIED"


def test_generate_decision_tree(client: TestClient):
    """Tests Mermaid flowchart compilation from transcript utterances."""
    utterances = [
        {
            "speaker": "Councillor Miller",
            "text": "I move that the proposed utility rate amendment be deferred to Q3.",
            "timestamp": 30.0,
            "confidence": 0.95,
        },
        {
            "speaker": "Mayor Clark",
            "text": "The motion is defeated.",
            "timestamp": 45.0,
            "confidence": 0.96,
        },
    ]

    response = client.post(
        "/api/v1/motions/generate-tree?meeting_title=Public%20Works%20Committee",
        json=utterances,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Public Works Committee"
    assert data["motion_count"] >= 1
    assert "flowchart TD" in data["mermaid_diagram"]


# ============================================================================
# 4. WebRTC Signaling & WebSocket Audio Chunk Ingestion (/api/v1/streaming)
# ============================================================================

def test_webrtc_signaling_flow(client: TestClient):
    """Tests SDP offer/answer exchange for WebRTC gateway."""
    meeting_id = "mtg-webrtc-test-01"

    # Step 1: Client submits SDP offer
    offer_payload = {
        "meeting_id": meeting_id,
        "sdp": "v=0\r\no=- 12345 2 IN IP4 127.0.0.1\r\ns=Client WebRTC\r\nm=audio 9 RTP/SAVPF 111\r\n",
        "type": "offer",
    }
    offer_res = client.post("/api/v1/streaming/webrtc/offer", json=offer_payload)
    assert offer_res.status_code == 200
    answer_data = offer_res.json()
    assert answer_data["meeting_id"] == meeting_id
    assert answer_data["type"] == "answer"
    assert "opus/48000" in answer_data["sdp"]

    # Step 2: Client acknowledges with answer
    answer_payload = {
        "meeting_id": meeting_id,
        "sdp": answer_data["sdp"],
        "type": "answer",
    }
    answer_res = client.post("/api/v1/streaming/webrtc/answer", json=answer_payload)
    assert answer_res.status_code == 200
    assert answer_res.json()["status"] == "connected"

    # Step 3: Check session status
    status_res = client.get(f"/api/v1/streaming/webrtc/session/{meeting_id}")
    assert status_res.status_code == 200
    assert status_res.json()["status"] == "ESTABLISHED"


def test_webrtc_invalid_offer(client: TestClient):
    """Verifies validation error handling for malformed WebRTC payloads."""
    res = client.post("/api/v1/streaming/webrtc/offer", json={"meeting_id": "", "sdp": ""})
    assert res.status_code == 400


def test_websocket_audio_ingestion(client: TestClient):
    """Tests WebSocket audio chunk streaming and acknowledgment."""
    meeting_id = "mtg-ws-audio-test-02"

    with client.websocket_connect(f"/api/v1/streaming/ws/audio/{meeting_id}") as websocket:
        # 1. Send Ping control message
        websocket.send_text("ping")
        reply = websocket.receive_text()
        assert reply == "pong"

        # 2. Stream binary audio PCM chunks (e.g., 512 bytes 16-bit PCM silence/tone)
        dummy_pcm = b"\x00\x05" * 256
        websocket.send_bytes(dummy_pcm)
        
        ack = websocket.receive_json()
        assert ack["type"] == "ack"
        assert ack["meeting_id"] == meeting_id
        assert ack["chunk_index"] == 1
        assert ack["bytes_received"] == len(dummy_pcm)
        assert ack["total_bytes"] == len(dummy_pcm)

        # Stream second chunk
        websocket.send_bytes(dummy_pcm)
        ack2 = websocket.receive_json()
        assert ack2["chunk_index"] == 2
        assert ack2["total_bytes"] == len(dummy_pcm) * 2


# ============================================================================
# 5. Statutory Municipal Bylaws & Procedure Tests (/api/v1/bylaws)
# ============================================================================

def test_list_procedure_rules(client: TestClient):
    """Tests listing all parliamentary and procedural rules and category filtering."""
    # List all rules
    res = client.get("/api/v1/bylaws/rules")
    assert res.status_code == 200
    rules = res.json()
    assert len(rules) >= 5
    assert any(r["rule_id"] == "RULE-001" for r in rules)

    # Filter by category
    filter_res = client.get("/api/v1/bylaws/rules?category=Governance")
    assert filter_res.status_code == 200
    filtered = filter_res.json()
    assert len(filtered) >= 1
    assert all(r["category"] == "Governance" for r in filtered)

    # Get single rule by ID
    single_res = client.get("/api/v1/bylaws/rules/RULE-001")
    assert single_res.status_code == 200
    assert single_res.json()["title"] == "Quorum of Council"

    # Non-existent rule ID
    not_found = client.get("/api/v1/bylaws/rules/RULE-NONEXISTENT")
    assert not_found.status_code == 404


def test_quorum_verification(client: TestClient):
    """Tests statutory quorum calculation under standard and custom thresholds."""
    # Scenario A: 7-member council, 4 members present -> Majority quorum met
    req_a = {"total_seats": 7, "present_members": 4}
    res_a = client.post("/api/v1/bylaws/quorum/verify", json=req_a)
    assert res_a.status_code == 200
    data_a = res_a.json()
    assert data_a["is_quorum_met"] is True
    assert data_a["required_seats"] == 4
    assert data_a["quorum_percentage"] == 57.14

    # Scenario B: 7-member council, 3 members present -> Quorum failed
    req_b = {"total_seats": 7, "present_members": 3}
    res_b = client.post("/api/v1/bylaws/quorum/verify", json=req_b)
    assert res_b.status_code == 200
    data_b = res_b.json()
    assert data_b["is_quorum_met"] is False
    assert data_b["required_seats"] == 4

    # Scenario C: Invalid count (present > total) -> Bad request
    req_c = {"total_seats": 5, "present_members": 6}
    res_c = client.post("/api/v1/bylaws/quorum/verify", json=req_c)
    assert res_c.status_code == 400


def test_speaking_timer_calculation(client: TestClient):
    """Tests speaking limits and warning timers based on council procedural roles."""
    # Public delegate (5 minutes = 300s)
    req_delegate = {"speaker": "Citizen Jane Doe", "role": "delegate"}
    res_delegate = client.post("/api/v1/bylaws/speaking-timer", json=req_delegate)
    assert res_delegate.status_code == 200
    data = res_delegate.json()
    assert data["allowed_seconds"] == 300
    assert data["warning_seconds"] == 60
    assert "Citizen Jane Doe" in data["message"]

    # Mayor (10 minutes = 600s)
    req_mayor = {"speaker": "Mayor HighRiver", "role": "mayor"}
    res_mayor = client.post("/api/v1/bylaws/speaking-timer", json=req_mayor)
    assert res_mayor.status_code == 200
    assert res_mayor.json()["allowed_seconds"] == 600

    # Custom override timer
    req_custom = {"speaker": "Special Consultant", "role": "presentation", "custom_limit_seconds": 1200}
    res_custom = client.post("/api/v1/bylaws/speaking-timer", json=req_custom)
    assert res_custom.status_code == 200
    assert res_custom.json()["allowed_seconds"] == 1200


# ============================================================================
# 6. Transcription Worker Queue & Audio Stream Processing Tests
# ============================================================================

@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_transcription_worker_lifecycle_and_processing():
    """Directly tests TranscriptionWorker queue ingestion and MotionExtractor dispatch."""
    worker = TranscriptionWorker()
    await worker.start()
    assert worker.running is True

    # Submit an audio job containing a motion phrase
    motion_text = "I move that the council approve the road repair budget for 2026."
    job = await worker.submit_audio(
        job_id="job-unit-001",
        meeting_id="mtg-unit-test",
        audio_pcm=motion_text.encode("utf-8"),
        speaker="Councillor Peterson",
        timestamp=10.5,
    )

    # Allow async queue consumer to process the item
    await asyncio.sleep(0.1)

    assert job.job_id in worker.processed_jobs
    processed = worker.processed_jobs[job.job_id]
    assert processed.processed is True
    assert processed.transcript == motion_text
    assert processed.motion is not None
    assert processed.motion.mover == "Councillor Peterson"
    assert "approve the road repair budget" in processed.motion.motion_text

    # Test callback mechanism
    callback_called = []
    worker.register_callback(lambda j: callback_called.append(j.job_id))

    await worker.submit_audio(
        job_id="job-unit-002",
        meeting_id="mtg-unit-test",
        audio_pcm=b"\x00\x02" * 128,
        speaker="Staff Member",
        timestamp=20.0,
    )
    await asyncio.sleep(0.1)

    assert "job-unit-002" in callback_called

    # Shutdown
    await worker.stop()
    assert worker.running is False
