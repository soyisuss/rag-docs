import logging
from pathlib import Path
from src.domain.ports.vector_store import VectorStorePort

logger = logging.getLogger(__name__)


class DeleteDocumentUseCase:
    """
    Deletes a document:
    1. Removes local file if it exists in data_dir.
    2. Purges all vectors associated with document_name from VectorStorePort.
    """

    def __init__(self, vector_store: VectorStorePort, data_dir: Path):
        self.vector_store = vector_store
        self.data_dir = data_dir

    def execute(self, document_name: str) -> bool:
        # 1. Remove file if exists
        target_file = self.data_dir / document_name
        if target_file.is_file():
            try:
                target_file.unlink()
                logger.info(f"Deleted local file: {target_file}")
            except Exception as e:
                logger.warning(f"Failed to delete local file {target_file}: {e}")

        # 2. Delete vectors from store
        self.vector_store.delete_by_document(document_name)
        logger.info(f"Purged vectors for document: {document_name}")
        return True
