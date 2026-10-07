<!-- Source: 08_Database_Schema_SignBridge_AI.docx | Converted from DOCX, all paragraphs/tables preserved -->

# DATABASE SCHEMA

## SignBridge AI – Indian Sign Language (ISL) Recognition System

| Field | Details |
| --- | --- |
| Document ID | 08_Database_Schema |
| Project | SignBridge AI |
| Document Type | Database Schema Specification |
| Version | 1.0 |
| Status | Draft / Editable |
| Database Type | Relational SQL database – [Confirm] |
| Recommended DB | PostgreSQL / MySQL – [Confirm] |
| Primary Purpose | Store application, sign, session, prediction, model and audit metadata |

## 1. Purpose

This document defines the logical and physical database structure for SignBridge AI. The database stores structured application metadata such as users, recognition sessions, ISL classes, model versions, prediction records, feedback, and system logs. Large raw videos and model files should normally remain in file/object storage rather than being stored directly inside relational tables.

## 2. Database Objectives

- Maintain a consistent master list of supported ISL signs/classes.
- Track recognition sessions and prediction events.
- Store model versions and deployment metadata.
- Support user feedback and error analysis.
- Provide traceability for API requests and system events.
- Maintain data integrity through primary keys, foreign keys, constraints, and indexes.
- Protect sensitive or personally identifiable information through data minimization.
## 3. Recommended Architecture

Frontend / Mobile
       ↓
API Service
       ↓
Application Database
       ├── Users
       ├── Sign Classes
       ├── Recognition Sessions
       ├── Predictions
       ├── Model Versions
       ├── Feedback
       └── Audit / API Logs

Object Storage
       ├── Raw Videos
       ├── Processed Files
       └── Dataset Artifacts

AI Model Storage
       └── Model Files / Weights

## 4. Database Scope

| Data Category | Stored in Database? | Notes |
| --- | --- | --- |
| User/application metadata | Yes | Only required fields |
| ISL class definitions | Yes | Master/reference data |
| Recognition sessions | Yes | Session metadata |
| Predictions | Yes | Structured prediction results |
| Model versions | Yes | Model registry metadata |
| User feedback | Yes | Optional evaluation data |
| API/system logs | Yes / separate log system | Retention policy required |
| Raw videos | Normally No | Use object/file storage |
| Images | Normally No | Store URI/reference if needed |
| Model weights | No | Use model/object storage |
| Landmark arrays | Optional | Prefer files/object storage for large volumes |

## 5. Entity Relationship Overview

USERS
  │
  └──< RECOGNITION_SESSIONS
          │
          └──< PREDICTIONS >── SIGN_CLASSES
                    │
                    └── MODEL_VERSIONS

PREDICTIONS ──< FEEDBACK

MODEL_VERSIONS ──< MODEL_DEPLOYMENTS

USERS / SESSIONS / PREDICTIONS ──< AUDIT_LOGS

## 6. Core Tables

| Table | Purpose | Primary Key |
| --- | --- | --- |
| users | Application user/account metadata | user_id |
| sign_classes | Supported ISL sign/class master data | class_id |
| recognition_sessions | Camera recognition session metadata | session_id |
| predictions | AI prediction records | prediction_id |
| model_versions | Registered AI model versions | model_id |
| model_deployments | Deployment/environment status | deployment_id |
| feedback | Optional user/evaluator feedback | feedback_id |
| api_logs | API request/response metadata | log_id |
| audit_logs | Security and administrative audit trail | audit_id |

## 7. Users Table

Table name: users

| Column | Type | Key | Nullable | Description |
| --- | --- | --- | --- | --- |
| user_id | UUID / BIGINT | PK | No | Unique user identifier |
| email | VARCHAR(255) | UNIQUE | Yes | Optional account email |
| display_name | VARCHAR(100) |  | Yes | User display name |
| role | VARCHAR(30) |  | No | user/admin/reviewer |
| status | VARCHAR(20) |  | No | active/inactive |
| created_at | TIMESTAMP |  | No | Account creation time |
| updated_at | TIMESTAMP |  | No | Last update time |

Note: the `users` table is intentionally kept (no endpoints yet) as the anchor for future auth work.

## 8. Sign Classes Table

Table name: sign_classes

| Column | Type | Key | Nullable | Description |
| --- | --- | --- | --- | --- |
| class_id | VARCHAR(50) | PK | No | Unique ISL class ID |
| label | VARCHAR(100) | UNIQUE | No | Canonical sign label |
| gloss | VARCHAR(100) |  | Yes | Optional standardized gloss |
| meaning | TEXT |  | Yes | English meaning/description |
| sign_type | VARCHAR(20) |  | No | static/dynamic |
| handedness | VARCHAR(20) |  | Yes | left/right/both/variable |
| description | TEXT |  | Yes | Additional sign description |
| is_active | BOOLEAN |  | No | Whether class is currently supported |
| created_at | TIMESTAMP |  | No | Creation time |
| updated_at | TIMESTAMP |  | No | Last update time |

## 9. Recognition Sessions Table

Table name: recognition_sessions

| Column | Type | Key | Nullable | Description |
| --- | --- | --- | --- | --- |
| session_id | UUID | PK | No | Unique recognition session |
| user_id | UUID / BIGINT | FK | Yes | Associated user |
| client_type | VARCHAR(30) |  | No | web/mobile/desktop |
| mode | VARCHAR(30) |  | No | isl_recognition |
| started_at | TIMESTAMP |  | No | Session start |
| ended_at | TIMESTAMP |  | Yes | Session end |
| status | VARCHAR(20) |  | No | active/closed/error |
| device_id | VARCHAR(100) |  | Yes | Anonymized device identifier |

## 10. Predictions Table

Table name: predictions

| Column | Type | Key | Nullable | Description |
| --- | --- | --- | --- | --- |
| prediction_id | UUID | PK | No | Unique prediction |
| session_id | UUID | FK | No | Recognition session |
| class_id | VARCHAR(50) | FK | Yes | Predicted sign class |
| model_id | UUID | FK | No | Model used |
| confidence | DECIMAL(6,5) |  | No | Prediction confidence 0–1 |
| status | VARCHAR(30) |  | No | recognized/uncertain/no_sign |
| sequence_id | VARCHAR(100) |  | Yes | Input sequence identifier |
| processing_time_ms | INTEGER |  | Yes | Inference processing time |
| created_at | TIMESTAMP |  | No | Prediction time |

## 11. Model Versions Table

Table name: model_versions

| Column | Type | Key | Nullable | Description |
| --- | --- | --- | --- | --- |
| model_id | UUID | PK | No | Unique registered model |
| model_name | VARCHAR(100) |  | No | Model name |
| version | VARCHAR(30) |  | No | Semantic/version identifier |
| model_type | VARCHAR(50) |  | No | LSTM/GRU/Transformer/etc. |
| framework | VARCHAR(30) |  | Yes | TensorFlow/PyTorch/etc. |
| input_sequence_length | INTEGER |  | Yes | Expected sequence length |
| feature_dimension | INTEGER |  | Yes | Features per frame |
| class_count | INTEGER |  | Yes | Number of supported classes |
| accuracy | DECIMAL(6,5) |  | Yes | Reported test accuracy |
| macro_f1 | DECIMAL(6,5) |  | Yes | Reported macro F1 |
| artifact_uri | TEXT |  | Yes | Model storage URI |
| status | VARCHAR(20) |  | No | development/staging/active/retired |
| created_at | TIMESTAMP |  | No | Registration time |

## 12. Model Deployments Table

Table name: model_deployments

| Column | Type | Key | Nullable | Description |
| --- | --- | --- | --- | --- |
| deployment_id | UUID | PK | No | Deployment identifier |
| model_id | UUID | FK | No | Deployed model |
| environment | VARCHAR(30) |  | No | dev/staging/production |
| endpoint | TEXT |  | Yes | Inference service endpoint |
| status | VARCHAR(20) |  | No | active/inactive |
| deployed_at | TIMESTAMP |  | No | Deployment time |
| retired_at | TIMESTAMP |  | Yes | Retirement time |

## 13. Feedback Table

Table name: feedback

| Column | Type | Key | Nullable | Description |
| --- | --- | --- | --- | --- |
| feedback_id | UUID | PK | No | Unique feedback record |
| prediction_id | UUID | FK | No | Related prediction |
| user_id | UUID / BIGINT | FK | Yes | Feedback provider |
| actual_class_id | VARCHAR(50) | FK | Yes | Correct class if known |
| feedback_type | VARCHAR(30) |  | No | correct/incorrect/uncertain |
| comment | TEXT |  | Yes | Optional explanation |
| created_at | TIMESTAMP |  | No | Feedback time |

## 14. API Logs Table

Table name: api_logs

| Column | Type | Key | Nullable | Description |
| --- | --- | --- | --- | --- |
| log_id | UUID | PK | No | Unique API log |
| request_id | VARCHAR(100) | INDEX | No | Request trace ID |
| session_id | UUID | FK | Yes | Associated session |
| endpoint | VARCHAR(255) |  | No | API endpoint |
| method | VARCHAR(10) |  | No | HTTP method |
| status_code | INTEGER |  | No | HTTP status |
| processing_time_ms | INTEGER |  | Yes | Server processing time |
| error_code | VARCHAR(50) |  | Yes | Application error code |
| created_at | TIMESTAMP |  | No | Request time |

## 15. Audit Logs Table

Table name: audit_logs

| Column | Type | Key | Nullable | Description |
| --- | --- | --- | --- | --- |
| audit_id | UUID | PK | No | Unique audit record |
| user_id | UUID / BIGINT | FK | Yes | Actor |
| action | VARCHAR(100) |  | No | Performed action |
| resource_type | VARCHAR(50) |  | No | Affected resource |
| resource_id | VARCHAR(100) |  | Yes | Affected resource ID |
| ip_hash | VARCHAR(255) |  | Yes | Privacy-preserving IP reference |
| created_at | TIMESTAMP |  | No | Action timestamp |

## 16. Relationships and Foreign Keys

| Relationship | Cardinality | Foreign Key |
| --- | --- | --- |
| users → recognition_sessions | 1 : Many | recognition_sessions.user_id |
| recognition_sessions → predictions | 1 : Many | predictions.session_id |
| sign_classes → predictions | 1 : Many | predictions.class_id |
| model_versions → predictions | 1 : Many | predictions.model_id |
| model_versions → model_deployments | 1 : Many | model_deployments.model_id |
| predictions → feedback | 1 : Many | feedback.prediction_id |
| users → feedback | 1 : Many | feedback.user_id |
| sign_classes → feedback | 1 : Many | feedback.actual_class_id |

## 17. Key Constraints

- Every primary key must be unique and non-null.
- Foreign-key references must point to existing records.
- Prediction confidence must be within 0.0 and 1.0.
- Model version identifiers should be unique within a model name.
- Class labels must be unique.
- Required timestamps must be stored in a consistent timezone, preferably UTC.
- Status fields should use controlled values or database enums/check constraints.
## 18. Indexing Strategy

| Table | Index | Purpose |
| --- | --- | --- |
| users | email | Fast account lookup |
| sign_classes | label | Fast label lookup |
| recognition_sessions | user_id, started_at | User session history |
| predictions | session_id, created_at | Session prediction retrieval |
| predictions | class_id | Class analytics |
| predictions | model_id | Model performance analysis |
| api_logs | request_id | Request tracing |
| api_logs | created_at | Time-based log queries |
| audit_logs | user_id, created_at | Audit history |

## 19. Normalization Strategy

The core relational schema should generally follow third-normal-form principles. Reusable reference data such as sign classes and model versions should not be duplicated unnecessarily in prediction records.

- Store class metadata in sign_classes rather than repeating full descriptions in predictions.
- Store model metadata in model_versions rather than duplicating architecture information in every prediction.
- Use foreign keys for relationships.
- Use separate feedback records rather than adding multiple feedback fields to predictions.
## 20. Example SQL DDL – Core Tables

CREATE TABLE sign_classes (
    class_id VARCHAR(50) PRIMARY KEY,
    label VARCHAR(100) NOT NULL UNIQUE,
    gloss VARCHAR(100),
    meaning TEXT,
    sign_type VARCHAR(20) NOT NULL,
    handedness VARCHAR(20),
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE model_versions (
    model_id UUID PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    version VARCHAR(30) NOT NULL,
    model_type VARCHAR(50) NOT NULL,
    framework VARCHAR(30),
    input_sequence_length INTEGER,
    feature_dimension INTEGER,
    class_count INTEGER,
    accuracy DECIMAL(6,5),
    macro_f1 DECIMAL(6,5),
    artifact_uri TEXT,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE recognition_sessions (
    session_id UUID PRIMARY KEY,
    user_id UUID,
    client_type VARCHAR(30) NOT NULL,
    mode VARCHAR(30) NOT NULL,
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    status VARCHAR(20) NOT NULL,
    device_id VARCHAR(100)
);

CREATE TABLE predictions (
    prediction_id UUID PRIMARY KEY,
    session_id UUID NOT NULL,
    class_id VARCHAR(50),
    model_id UUID NOT NULL,
    confidence DECIMAL(6,5) NOT NULL,
    status VARCHAR(30) NOT NULL,
    sequence_id VARCHAR(100),
    processing_time_ms INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (session_id) REFERENCES recognition_sessions(session_id),
    FOREIGN KEY (class_id) REFERENCES sign_classes(class_id),
    FOREIGN KEY (model_id) REFERENCES model_versions(model_id)
);

## 21. Data Retention

| Data | Suggested Retention | Project Value |
| --- | --- | --- |
| User account metadata | While account active + policy period | [Enter] |
| Recognition sessions | 30–180 days or project policy | [Enter] |
| Prediction records | 30–365 days or research policy | [Enter] |
| API logs | 30–90 days | [Enter] |
| Audit logs | Per security policy | [Enter] |
| Feedback | Until research/evaluation need ends | [Enter] |

## 22. Privacy and Security

- Store only the minimum user information required by the application.
- Prefer anonymized IDs for signers and devices.
- Do not store raw camera/video data in the relational database unless explicitly required.
- Encrypt database connections in production.
- Apply role-based database access.
- Protect credentials using environment variables or a secrets manager.
- Define retention and deletion procedures.
- Remove or hash network identifiers where full values are not required.
## 23. Backup and Recovery

| Requirement | Specification | Project Value |
| --- | --- | --- |
| Database backup | Automated scheduled backup | [Enter] |
| Backup frequency | Daily minimum for production | [Enter] |
| Recovery testing | Periodic restore test | [Enter] |
| Backup encryption | Required | [Enter] |
| Retention | Defined by project policy | [Enter] |
| Disaster recovery | Document restore procedure | [Enter] |

## 24. Performance Requirements

| Metric | Target | Actual |
| --- | --- | --- |
| Prediction record insert | < 100 ms preferred | [Enter] |
| Session lookup | < 100 ms preferred | [Enter] |
| Class lookup | < 50 ms preferred | [Enter] |
| Prediction history query | < 500 ms preferred | [Enter] |
| Database availability | ≥ 99% target for production | [Enter] |

## 25. Dataset and Database Separation

The training dataset and production application database should be treated as separate data domains. Dataset files, landmarks, annotations, and model artifacts should use versioned file/object storage. The database should store metadata and references to those artifacts where necessary.

## 26. Database Migration Strategy

- Version every schema change.
- Use migration scripts rather than manual production edits.
- Test migrations against a staging database.
- Maintain backward compatibility where possible.
- Back up the database before destructive migrations.
- Record migration version and execution time.
## 27. Editable Database Configuration

| Parameter | Current Value |
| --- | --- |
| Database engine | PostgreSQL / MySQL – [Confirm] |
| Database name | [Enter] |
| Host | [Enter] |
| Port | [Enter] |
| ORM | SQLAlchemy / Prisma / Django ORM – [Confirm] |
| Migration tool | Alembic / Flyway / Prisma – [Confirm] |
| Connection pooling | [Enter] |
| Backup frequency | [Enter] |
| Retention period | [Enter] |
| Schema version | v1.0 |

## 28. Database Testing Checklist

☐ Primary-key constraints tested.

☐ Foreign-key constraints tested.

☐ Unique constraints tested.

☐ Invalid confidence values rejected.

☐ Invalid status values rejected.

☐ Indexes verified for common queries.

☐ Migration scripts tested.

☐ Backup and restore tested.

☐ Unauthorized database access prevented.

☐ Retention/deletion procedures tested.

## 29. Dependencies on Other Documents

- 01_Project_PRD – product requirements.
- 02_SRS – functional and non-functional requirements.
- 03_System_Architecture – component and data-flow architecture.
- 04_Dataset_Specification – dataset metadata and versioning.
- 05_AI_Model_Specification – model and prediction metadata.
- 06_Preprocessing_Feature_Engineering – processed data and feature definitions.
- 07_API_Contract – API data objects and request/response requirements.
- 09_UI_UX_Specification – frontend data requirements.
## 30. Version History

| Version | Change | Date | Owner |
| --- | --- | --- | --- |
| v1.0 | Initial database schema specification | [Enter] | [Enter] |
| v1.1 | [Future compatible change] | [Enter] | [Enter] |
| v2.0 | [Future schema revision] | [Enter] | [Enter] |

## 31. Approval

| Role | Name | Signature | Date |
| --- | --- | --- | --- |
| Backend/Database Lead | [Enter name] | ________________ | ____________ |
| AI/ML Lead | [Enter name] | ________________ | ____________ |
| Project Lead | [Enter name] | ________________ | ____________ |
| Project Guide | [Enter name] | ________________ | ____________ |
