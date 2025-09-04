from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class ValidationStatus(str, Enum):
    UNVERIFIED = "unverified"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EDITED = "edited"

class CorrectionMetadata(BaseModel):
    status: ValidationStatus = Field(default=ValidationStatus.UNVERIFIED)
    reviewer_comment: Optional[str] = Field(None)
    last_reviewed: Optional[datetime] = Field(None)

class Provenance(BaseModel):
    source_filename: str = Field(...)
    page_number: int = Field(...)
    line_number: Optional[int] = Field(None)
    bounding_box: Optional[List[float]] = Field(None)

class PICO(BaseModel):
    population: Optional[str] = Field(None)
    intervention: Optional[str] = Field(None)
    comparison: Optional[str] = Field(None)
    outcome: Optional[str] = Field(None)
    provenance: List[Provenance] = Field(default_factory=list)
    correction_metadata: CorrectionMetadata = Field(default_factory=CorrectionMetadata)

class QualityScore(BaseModel):
    score_name: str = Field(...)
    score_value: str = Field(...)
    justification: Optional[str] = Field(None)
    provenance: Optional[Provenance] = Field(None)
    correction_metadata: CorrectionMetadata = Field(default_factory=CorrectionMetadata)

class Claim(BaseModel):
    claim_text: str = Field(...)
    linked_citations: List[str] = Field(default_factory=list)
    provenance: Provenance
    uncertainty_annotation: Optional[str] = Field(None)
    correction_metadata: CorrectionMetadata = Field(default_factory=CorrectionMetadata)

class ExtractedTable(BaseModel):
    summary: Optional[str] = Field(None, description="An AI-generated summary of the table's main finding.")
    table_data: List[Dict[str, Any]] = Field(
        ...,
        description="The table content, represented as a list of rows, where each row is a dictionary."
    )
    provenance: Provenance
    correction_metadata: CorrectionMetadata = Field(default_factory=CorrectionMetadata)

class ExtractedFigure(BaseModel):
    caption: str = Field(...)
    figure_type: str = Field(...)
    provenance: Provenance
    correction_metadata: CorrectionMetadata = Field(default_factory=CorrectionMetadata)

class BibliographyItem(BaseModel):
    citation_key: str = Field(...)
    full_citation: str = Field(...)

class ArticleExtraction(BaseModel):
    source_filename: str
    title: Optional[str] = None
    authors: List[str] = Field(default_factory=list)
    summary: Optional[str] = Field(None)
    records_excluded_count: int = Field(default=0)
    claims: List[Claim] = Field(default_factory=list)
    pico_elements: Optional[PICO] = None
    quality_scores: List[QualityScore] = Field(default_factory=list)
    tables: List[ExtractedTable] = Field(default_factory=list)
    figures: List[ExtractedFigure] = Field(default_factory=list)
    bibliography: Dict[str, BibliographyItem] = Field(default_factory=dict)