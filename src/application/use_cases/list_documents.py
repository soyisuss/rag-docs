from pathlib import Path
from typing import List
from src.application.dtos import DocumentItemDTO
from src.domain.ports.vector_store import VectorStorePort


class ListDocumentsUseCase:
    """
    Lists all available documents by consolidating both local files and vector database entries.
    """

    def __init__(self, vector_store: VectorStorePort, data_dir: Path):
        self.vector_store = vector_store
        self.data_dir = data_dir

    def execute(self) -> List[DocumentItemDTO]:
        local_files = set()
        if self.data_dir.is_dir():
            local_files = {f.name for f in self.data_dir.glob("*.pdf")}

        try:
            vector_docs = set(self.vector_store.list_indexed_document_names())
        except Exception:
            vector_docs = set()

        all_names = sorted(local_files.union(vector_docs))
        return [
            DocumentItemDTO(
                name=name,
                in_storage=name in local_files,
                in_vector_store=name in vector_docs,
            )
            for name in all_names
        ]
