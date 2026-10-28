import shutil
from pathlib import Path
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException

from src.presentation.schemas import (
    DocumentListResponse,
    DocumentResponse,
    UploadResponse,
    DeleteResponse,
)
from src.application.use_cases.list_documents import ListDocumentsUseCase
from src.application.use_cases.ingest_document import IngestDocumentUseCase
from src.application.use_cases.delete_document import DeleteDocumentUseCase
from src.presentation.dependencies import (
    get_list_use_case,
    get_ingest_use_case,
    get_delete_use_case,
    get_data_dir,
)

router = APIRouter(prefix="/api/documents", tags=["Documents"])


@router.get("", response_model=DocumentListResponse)
def list_documents(
    use_case: ListDocumentsUseCase = Depends(get_list_use_case),
) -> DocumentListResponse:
    docs = use_case.execute()
    return DocumentListResponse(
        total=len(docs),
        documents=[
            DocumentResponse(
                name=d.name,
                in_storage=d.in_storage,
                in_vector_store=d.in_vector_store,
            )
            for d in docs
        ],
    )


@router.post("/upload", response_model=UploadResponse)
def upload_documents(
    files: List[UploadFile] = File(...),
    ingest_use_case: IngestDocumentUseCase = Depends(get_ingest_use_case),
    data_dir: Path = Depends(get_data_dir),
) -> UploadResponse:
    if not files:
        raise HTTPException(status_code=400, detail="No se enviaron archivos para procesar.")

    uploaded_names: List[str] = []
    total_chunks = 0

    for file in files:
        if not file.filename or not file.filename.lower().endswith(".pdf"):
            continue

        target_path = data_dir / file.filename
        with open(target_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        ingest_result = ingest_use_case.execute(target_path)
        if ingest_result.success:
            uploaded_names.append(file.filename)
            total_chunks += ingest_result.chunks_indexed

    if not uploaded_names:
        raise HTTPException(
            status_code=400, 
            detail="Ningún archivo PDF válido fue procesado."
        )

    return UploadResponse(
        uploaded=uploaded_names,
        total_chunks=total_chunks,
        message=f"Se procesaron {len(uploaded_names)} documentos con éxito ({total_chunks} fragmentos indexados).",
    )


@router.delete("/{doc_name}", response_model=DeleteResponse)
def delete_document(
    doc_name: str,
    delete_use_case: DeleteDocumentUseCase = Depends(get_delete_use_case),
) -> DeleteResponse:
    success = delete_use_case.execute(doc_name)
    return DeleteResponse(
        document_name=doc_name,
        deleted=success,
        message=f"Documento '{doc_name}' y sus vectores asociados han sido eliminados.",
    )
