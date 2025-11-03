APP_NAME = "mini-RAG"
APP_VERSION = "0.1"
OPENAI_API_KEY = ""

FILE_ALLOWED_TYPES = ["text/plain", "application/pdf"]
FILE_MAX_SIZE = 10 # MB
FILE_DEFAULT_CHUNCK_SIZE = 512000 # 512KB

POSTGRES_USERNAME = "postgres"
POSTGRES_PASSWORD = "postgres_password"
POSTGRES_HOT = "pgvector"
POSTGRES_PORT = 5432
POSTGRES_MAIN_DATABASE = "minirag"

# ====================== LLM Config =========================
GENERATION_BACKEND = "COHERE"# OPENAI
EMBEDDING_BACKEND = "COHERE"

OPENAI_API_KEY = ""
OPENAI_API_URL = ""
COHERE_API_KEY = "key___"

GENERATION_MODEL_ID_LITERAL = ["command-r-plus-08-2024", "gemma2:9b-instruct-q5_0"]
GENERATION_MODEL_ID = "command-r-plus-08-2024"
EMBEDDING_MODEL_ID = "embed-multilingual-v3.0"
EMBEDDING_MODEL_SIZE = 1024

INPUT_DAFAULT_MAX_CHARACTERS = 1024
GENERATION_DAFAULT_MAX_TOKENS = 200
GENERATION_DAFAULT_TEMPERATURE = 0.1

# ====================== Vector DB Config =========================
VECTOR_DB_BACKEND_LITERAL = ["QDRANT", "PGVECTOR"]
VECTOR_DB_BACKEND = "PGVECTOR"
VECTOR_DB_PATH = "qdrant_db"
VECTOR_DB_DISTANCE_METHOD = "cosine"
VECTOR_DB_PGVEC_INDEX_THRESHOLD = 50

# ====================== Template Configs =========================
PRIMARY_LANG = "ar"
DEFAULT_LANG = "en"
