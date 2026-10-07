<!-- Source: 07_API_Contract_SignBridge_AI.docx | Converted from DOCX, all paragraphs/tables preserved -->

# API CONTRACT

## SignBridge AI – Indian Sign Language (ISL) Recognition System

| Field | Details |
| --- | --- |
| Document ID | 07_API_Contract |
| Project | SignBridge AI |
| Document Type | API Contract / Interface Specification |
| Version | 1.0 |
| Status | Draft / Editable |
| API Style | REST/JSON + optional WebSocket for real-time streaming |
| Primary Consumer | Web / mobile frontend and application services |
| Primary Provider | Sign recognition backend / AI inference service |

## 1. Purpose

This document defines the application programming interfaces used by SignBridge AI to connect the user interface, preprocessing services, AI inference service, database, and optional speech/text components. It establishes consistent request and response formats so that frontend and backend components can be developed and tested independently.

## 2. API Objectives

- Provide a stable interface for real-time ISL recognition.
- Accept image/frame or processed landmark input according to the deployment architecture.
- Return predicted sign labels, confidence, and recognition status.
- Support health checks and model information for operational monitoring.
- Provide structured error responses.
- Allow future integration with text-to-speech and text-to-sign components.
## 3. API Architecture

Recommended integration:

Frontend / Web / Mobile
        │
        ├── REST API ───────────────┐
        │                           │
        └── WebSocket (optional)    │
                                    ↓
                         SignBridge API Gateway
                                    ↓
                         Validation / Preprocessing
                                    ↓
                           AI Inference Service
                                    ↓
                         Prediction / Post-process
                                    ↓
                         Response to Client

## 4. Base Configuration

| Parameter | Recommended Value | Project Value |
| --- | --- | --- |
| Base URL | https://<domain>/api/v1 | [Enter] |
| Protocol | HTTPS | [Confirm] |
| REST format | JSON | [Confirm] |
| Real-time protocol | WebSocket – optional | [Confirm] |
| Character encoding | UTF-8 | [Confirm] |
| API version | v1 | v1 |
| Default timeout | 5–10 seconds REST | [Enter] |
| Real-time timeout | Application dependent | [Enter] |

## 5. API Versioning

The API should use explicit versioning to prevent breaking changes from silently affecting clients.

/api/v1/<resource>

Breaking changes should result in a new API version. Backward-compatible additions may remain within the current version.

## 6. Authentication and Authorization

| Requirement | Specification |
| --- | --- |
| Public demo | May use restricted unauthenticated access |
| Production API | API key, JWT, or OAuth2 – [Confirm] |
| Transport security | HTTPS/TLS required in production |
| Token storage | Never expose secrets in client code |
| Rate limiting | Required for public/production endpoints |
| Authorization | Role-based access where administrative endpoints exist |

## 7. Content Types

| Request Type | Content-Type |
| --- | --- |
| JSON request | application/json |
| Image upload | multipart/form-data |
| Video upload | multipart/form-data |
| WebSocket message | JSON text or binary frame – [Confirm] |

## 8. Endpoint Summary

| Method | Endpoint | Purpose | Auth |
| --- | --- | --- | --- |
| GET | /health | Service health check | No / restricted |
| GET | /api/v1/model | Get active model information | Optional |
| POST | /api/v1/predict | Recognize a sign from image/features (unknown non-empty `session_id` → 404 `UNKNOWN_SESSION`) | Yes |
| POST | /api/v1/predict/sequence | Recognize a temporal sequence | Yes |
| POST | /api/v1/session | Create recognition session | Yes |
| DELETE | /api/v1/session/{id} | End recognition session (stored row marked `closed`) | Yes |
| DELETE | /api/v1/sessions/{id}/purge | Permanently delete session + its predictions + feedback (404 unknown) | Yes |
| POST | /api/v1/feedback | Submit feedback for a prediction `{prediction_id, actual_class_id?, rating?}` → 200 + row (404 unknown prediction) | Yes |
| WS | /api/v1/stream | Real-time recognition stream | Yes |
| GET | /api/v1/classes | Get supported sign classes | Optional |

Note: `POST /api/v1/admin/rollback` swaps `active_model` ↔ `previous_model` in
`models/registry.json` (audit-logged) and returns the restored `model_id`; with no
`previous_model` recorded it returns `404` with `error.code: NO_ROLLBACK_STATE`.

## 9. Health Check API

Endpoint: GET /health

Response 200
{
  "status": "ok",
  "service": "signbridge-api",
  "version": "1.0.0",
  "timestamp": "2026-09-27T12:00:00Z"
}

Purpose: Verify that the API service is running and reachable.

## 10. Model Information API

Endpoint: GET /api/v1/model

Response 200
{
  "model_id": "signbridge-lstm-v1",
  "model_version": "1.0.0",
  "model_type": "LSTM",
  "classes": 50,
  "input_sequence_length": 45,
  "feature_dimension": 189,
  "status": "active"
}

The actual values must match the deployed model configuration.

> **Registry/policy caching:** `read_registry`/`get_policy` (and the class list) are
> cached in-process; edits to `models/registry.json`, `policy.json`, or `class_map.csv`
> take effect on service restart (restart picks up CSV/registry edits).

## 11. Single Prediction API

Endpoint: POST /api/v1/predict

Purpose: Predict an ISL sign from a single frame or prepared feature representation.

Request
{
  "session_id": "sess_001",
  "input_type": "landmarks",
  "features": [0.12, -0.04, 0.33, "..."],
  "timestamp": "2026-09-27T12:00:01Z"
}

Response 200
{
  "success": true,
  "prediction": {
    "class_id": "ISL_001",
    "label": "HELLO",
    "confidence": 0.96
  },
  "status": "recognized",
  "model_version": "1.0.0"
}

## 12. Sequence Prediction API

Endpoint: POST /api/v1/predict/sequence

Purpose: Recognize dynamic signs from an ordered temporal feature sequence.

Request
{
  "session_id": "sess_001",
  "sequence_id": "seq_1001",
  "sequence_length": 45,
  "feature_dimension": 189,
  "frames": [
    [0.12, 0.08, 0.31, "..."],
    [0.13, 0.08, 0.32, "..."]
  ]
}

Response 200
{
  "success": true,
  "prediction": {
    "class_id": "ISL_014",
    "label": "THANK_YOU",
    "confidence": 0.93
  },
  "status": "recognized",
  "sequence_id": "seq_1001",
  "model_version": "1.0.0"
}

## 13. Image Upload Prediction

Endpoint: POST /api/v1/predict/image

Request
Content-Type: multipart/form-data

file=<image>
session_id=sess_001

Response
{
  "success": true,
  "prediction": {
    "class_id": "ISL_001",
    "label": "HELLO",
    "confidence": 0.91
  },
  "status": "recognized"
}

> **STUB (owner: P8 container work) — contract only, stays 501:** `POST /api/v1/predict/image`
> currently returns `501` with `error.code: CV_UNAVAILABLE` ("MediaPipe image pipeline
> requires the py3.11 container (P8); use /predict with landmarks until then"). The
> schema above describes the intended future response, not current behavior.

## 14. Video Upload Prediction

Endpoint: POST /api/v1/predict/video

Request
Content-Type: multipart/form-data

file=<video>
session_id=sess_001

Response
{
  "success": true,
  "prediction": {
    "class_id": "ISL_014",
    "label": "THANK_YOU",
    "confidence": 0.94
  },
  "status": "recognized",
  "processing_time_ms": 184
}

> **STUB (owner: P8 container work) — contract only, stays 501:** `POST /api/v1/predict/video`
> currently returns `501` with `error.code: CV_UNAVAILABLE` ("MediaPipe video pipeline
> requires the py3.11 container (P8); use /predict/sequence with landmarks until then").
> The schema above describes the intended future response, not current behavior.

For large videos, asynchronous processing may be preferable. The exact maximum upload size must be configured by deployment.

## 15. Recognition Session API

Endpoint: POST /api/v1/session

Request
{
  "client_type": "web",
  "language": "en",
  "mode": "isl_recognition"
}

Response 201
{
  "session_id": "sess_001",
  "status": "active",
  "expires_in": 3600
}

## 16. End Recognition Session

Endpoint: DELETE /api/v1/session/{session_id}

Response 200
{
  "success": true,
  "session_id": "sess_001",
  "status": "closed"
}

## 17. Supported Classes API

Endpoint: GET /api/v1/classes

Response 200
{
  "classes": [
    {
      "class_id": "ISL_001",
      "label": "HELLO",
      "type": "static"
    },
    {
      "class_id": "ISL_002",
      "label": "THANK_YOU",
      "type": "dynamic"
    }
  ]
}

## 18. Real-Time WebSocket API

The WebSocket interface is intended for low-latency camera interaction. The client maintains a connection and sends frame-derived features or frames according to the selected architecture.

Connection
wss://<domain>/api/v1/stream?session_id=sess_001

`session_id` must already exist (created via `POST /api/v1/session`); unknown/missing IDs get `{"type":"error","code":"UNKNOWN_SESSION"}` and the socket is closed with 4404 — nothing is created.

Client message
{
  "type": "frame",
  "sequence_index": 42,
  "timestamp": "2026-09-27T12:00:02.100Z",
  "features": [0.12, 0.08, 0.31, "..."]
}

Server message
{
  "type": "prediction",
  "class_id": "ISL_014",
  "label": "THANK_YOU",
  "confidence": 0.94,
  "status": "recognized"
}

## 19. WebSocket Message Types

| Message Type | Direction | Purpose |
| --- | --- | --- |
| start | Client → Server | Start recognition |
| frame | Client → Server | Send frame/features |
| prediction | Server → Client | Return prediction |
| status | Server → Client | Tracking/service status |
| error | Server → Client | Report processing error |
| stop | Client → Server | End recognition |
| heartbeat | Both | Keep connection active |

## 20. Standard Prediction Schema

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| success | boolean | Yes | Whether request was processed |
| class_id | string | If recognized | Internal sign class |
| label | string | If recognized | Human-readable sign |
| confidence | number | If recognized | 0–1 confidence value |
| status | string | Yes | recognized / uncertain / no_sign / error |
| model_version | string | Recommended | Model used for prediction |
| timestamp | string | Recommended | Prediction timestamp |
| processing_time_ms | number | Optional | Backend processing time |

## 21. Recognition Status Values

| Status | Meaning |
| --- | --- |
| recognized | Prediction passed configured confidence criteria |
| uncertain | Model produced a prediction below confidence threshold |
| no_sign | No valid sign/tracking detected |
| tracking_lost | Required landmarks unavailable |
| processing | Input is being processed |
| error | Request could not be processed |

No-sign uses REST status `no-sign` / WS state `No-Sign` with sentinel prediction `{"class_id": "ISL_000", "label": "No sign detected", "confidence": 0.0}` (never persisted; `prediction_id` is `""`).

## 22. Error Response Contract

{
  "success": false,
  "error": {
    "code": "INVALID_INPUT",
    "message": "Feature dimension does not match model input.",
    "details": {
      "expected": 189,
      "received": 120
    }
  },
  "request_id": "req_001"
}

### Envelope scope

The `{success: false, error: {code, message, details}, request_id}` envelope applies to
errors raised or returned by matched routes: raised `401 UNAUTHORIZED` / `403 FORBIDDEN` /
`429 RATE_LIMITED` (via the `HTTPException` handler) and endpoint-built `404` / `422` /
`413` / `501` JSON bodies. Unknown-route 404s never reach a route and stay
Starlette-plain (`{"detail": "Not Found"}`) — clients must handle both shapes.

## 23. HTTP Status Codes

| Code | Meaning | Example |
| --- | --- | --- |
| 200 | Success | Prediction returned |
| 201 | Created | Session created |
| 400 | Bad Request | Invalid JSON/input |
| 401 | Unauthorized | Missing/invalid token |
| 403 | Forbidden | Insufficient permission |
| 404 | Not Found | Unknown endpoint/session |
| 408 | Request Timeout | Processing timeout |
| 413 | Payload Too Large | Upload exceeds limit |
| 415 | Unsupported Media Type | Invalid file format |
| 422 | Validation Error | Schema/feature validation failed |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Unexpected backend error |
| 501 | Not Implemented | Stubbed endpoint (tts / predict image / video) |
| 503 | Service Unavailable | Model/service unavailable |

## 24. Request Validation

- Validate JSON schema before inference.
- Validate sequence length and feature dimension.
- Reject NaN, infinite, or malformed numerical values.
- Validate supported media types and file sizes.
- Validate session identifiers where session-based APIs are used.
- Reject unsupported class IDs or model versions when explicitly supplied.
## 25. Rate Limiting

| Client Type | Suggested Policy | Project Value |
| --- | --- | --- |
| Web/mobile user | Application-specific limit | [Enter] |
| Public API | Per-IP / token limit | [Enter] |
| WebSocket | Frame/message rate limit | [Enter] |
| Admin | Higher controlled limit | [Enter] |

Rate limits should prevent accidental overload while preserving sufficient throughput for real-time recognition.

## 26. Security Requirements

- Use HTTPS/TLS for production REST APIs.
- Use secure WebSocket connections (WSS) in production.
- Validate and sanitize uploaded files.
- Limit request payload size.
- Do not expose model files or internal server paths through API responses.
- Avoid storing raw camera data unless explicitly required and authorized.
- Do not include personally identifiable information in prediction logs.
## 27. Logging and Observability

| Log Field | Purpose |
| --- | --- |
| request_id | Trace individual request |
| session_id | Trace recognition session |
| timestamp | Event timing |
| endpoint | API operation |
| model_version | Identify deployed model |
| processing_time_ms | Performance monitoring |
| status | Prediction/request outcome |
| error_code | Failure analysis |

## 28. API Performance Requirements

| Metric | Target | Actual |
| --- | --- | --- |
| REST response latency | < 500 ms preferred | [Enter] |
| Real-time inference latency | < 200 ms preferred | [Enter] |
| WebSocket responsiveness | Suitable for live interaction | [Enter] |
| Availability | ≥ 99% target for production | [Enter] |
| Payload validation | Before inference | [Enter] |

## 29. API-to-Model Data Contract

| API Field | Model Field |
| --- | --- |
| sequence_length | Temporal sequence length |
| feature_dimension | Feature vector size |
| frames | Model input tensor |
| model_version | Loaded model identifier |
| confidence | Prediction probability |
| class_id | Model output class index |
| label | Class mapping result |

## 30. Text and Speech Integration

The API may be extended to support downstream communication features. A recognized ISL label can be passed to a text-generation or text-to-speech service.

| Future Endpoint | Purpose |
| --- | --- |
| POST /api/v1/text | Convert recognized sign sequence into text |
| POST /api/v1/speech | Convert generated text into speech |
| POST /api/v1/sign | Convert text into sign-language representation/animation |

> **STUB (owner: P5 wiring) — contract only, stays 501:** `POST /api/v1/tts` currently
> returns `501` with `error.code: TTS_NOT_CONFIGURED` ("Speech engine not configured
> (P5 wiring); text echoed for contract testing"). `POST /api/v1/text-to-sign` is
> implemented (phrase-aware lookup against seeded sign assets, unsupported words
> reported explicitly) and is NOT a stub.

## 31. API Testing Requirements

☐ Unit-test request validation.

☐ Test valid and invalid prediction payloads.

☐ Test missing and malformed fields.

☐ Test authentication failures.

☐ Test oversized uploads.

☐ Test model unavailable conditions.

☐ Test WebSocket connection and reconnect behavior.

☐ Test response schema consistency.

☐ Load-test real-time endpoints within expected concurrency.

## 32. Example End-to-End Flow

1. Frontend requests a recognition session.

2. Backend returns a session ID.

3. Frontend captures camera frames.

4. Preprocessing extracts/normalizes landmarks.

5. Frontend or backend sends model-ready sequence data.

6. AI inference service predicts the sign.

7. Backend applies confidence and temporal rules.

8. API returns the recognized label and confidence.

9. Frontend displays the sign as text and optionally sends it to speech output.

## 33. Editable API Configuration

| Parameter | Current Value |
| --- | --- |
| Base URL | [Enter] |
| API version | v1 |
| Authentication | [Enter] |
| REST framework | FastAPI / Flask / Node.js – [Confirm] |
| WebSocket support | Yes / No – [Confirm] |
| Maximum image size | [Enter] |
| Maximum video size | [Enter] |
| REST timeout | [Enter] |
| Rate limit | [Enter] |
| Confidence threshold | [Enter] |
| Model version | [Enter] |
| API contract version | 1.0 |

## 34. API Acceptance Checklist

☐ All endpoints have documented request and response schemas.

☐ Authentication and authorization behavior is defined.

☐ Validation rules are implemented.

☐ Standard error responses are implemented.

☐ Model prediction endpoint works with the finalized model.

☐ Real-time WebSocket behavior is tested if enabled.

☐ Rate limiting is configured.

☐ HTTPS/WSS is enabled in production.

☐ Logging and request tracing are implemented.

☐ API versioning is documented.

## 35. Dependencies on Other Documents

- 01_Project_PRD – product and feature requirements.
- 02_SRS – functional and non-functional requirements.
- 03_System_Architecture – system components and communication flow.
- 04_Dataset_Specification – input data and labels.
- 05_AI_Model_Specification – model input/output and inference requirements.
- 06_Preprocessing_Feature_Engineering – model-ready feature pipeline.
- 08_Database_Schema – persistent data structures where applicable.
- 09_UI_UX_Specification – frontend integration requirements.
## 36. Version History

| Version | Change | Date | Owner |
| --- | --- | --- | --- |
| v1.0 | Initial API contract | [Enter] | [Enter] |
| v1.1 | [Future compatible changes] | [Enter] | [Enter] |
| v2.0 | [Future breaking changes] | [Enter] | [Enter] |

## 37. Approval

| Role | Name | Signature | Date |
| --- | --- | --- | --- |
| Backend/API Lead | [Enter name] | ________________ | ____________ |
| AI/ML Lead | [Enter name] | ________________ | ____________ |
| Frontend Lead | [Enter name] | ________________ | ____________ |
| Project Guide | [Enter name] | ________________ | ____________ |

## 38. Environment contract
Backend auto-loads `backend/.env` then repo-root `.env` at `import app` time (`python-dotenv`; explicit process env wins; resolved file logged).
Compose runs `APP_ENV=production` and fails fast without `JWT_SECRET` / `POSTGRES_PASSWORD` (`${VAR:?msg}`); `DATABASE_URL` interpolates the DB password.
`APP_ENV=production` + default `JWT_SECRET=change-me` refuses to boot (`create_app` raises `RuntimeError`); tests pin `JWT_SECRET=test-secret` via `tests/conftest.py`.
 4-origin `CORS_ORIGINS`: `http://localhost:3000,http://localhost:5173,http://127.0.0.1:5173,http://127.0.0.1:3000`.
`APP_ENV=production` disables the interactive docs (`/docs`, `/redoc`, `/openapi.json` return 404; `create_app` gates on `APP_ENV` at call time, same pattern as the prod-secret guard).
Every response carries minimal security headers: `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: no-referrer`.
Frontend `VITE_API_BASE` falls back to `http://localhost:8000` on unset OR empty string (`||`, not `??`).
