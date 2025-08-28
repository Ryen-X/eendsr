from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class ValidationStatus(str, Enum):
    UNVERIFIED = "unverified"
    VERIFIED = "verified"
    REJECTED = "rejected"
    EDITED = "edited"

class CorrectionMetadata(BaseModel):
    status: ValidationStatus = Field(
        default=ValidationStatus.UNVERIFIED,
        description="The validation status of this item, set by a human reviewer."
    )
    reviewer_comment: Optional[str] = Field(
        None,
        description="A comment or note from the human reviewer."
    )
    last_reviewed: Optional[datetime] = Field(
        None,
        description="The timestamp of the last human review."
    )

class Provenance(BaseModel):
    source_filename: str = Field(..., description="The name of the source PDF file.")
    page_number: int = Field(..., description="The page number where the information was found.")
    line_number: Optional[int] = Field(None, description="An approximate line number on the page.")
    bounding_box: Optional[List[float]] = Field(
        None,
        description="A list of coordinates [x0, y0, x1, y1] defining the object's location."
    )

class PICO(BaseModel):
    population: Optional[str] = Field(None, description="The characteristics of the study population.")
    intervention: Optional[str] = Field(None, description="The intervention or treatment being studied.")
    comparison: Optional[str] = Field(None, description="The control or comparison group.")
    outcome: Optional[str] = Field(None, description="The outcomes measured in the study.")
    provenance: List[Provenance] = Field(
        default_factory=list,
        description="List of sources for the PICO elements."
    )
    correction_metadata: CorrectionMetadata = Field(default_factory=CorrectionMetadata)

class QualityScore(BaseModel):
    score_name: str = Field(..., description="The name of the quality scoring system (e.g., 'Jadad', 'RoB 2').")
    score_value: str = Field(..., description="The calculated score or rating.")
    justification: Optional[str] = Field(None, description="The justification or evidence for the assigned score.")
    provenance: Optional[Provenance] = Field(None, description="The source of the quality score information, if applicable.")
    correction_metadata: CorrectionMetadata = Field(default_factory=CorrectionMetadata)

class Claim(BaseModel):
    claim_text: str = Field(..., description="The verbatim text of the extracted claim.")
    linked_citations: List[str] = Field(
        default_factory=list,
        description="A list of citation keys (e.g., 'Author2023') linked to this claim."
    )
    provenance: Provenance
    uncertainty_annotation: Optional[str] = Field(
        None,
        description="A human-readable annotation about the confidence in this claim."
    )
    correction_metadata: CorrectionMetadata = Field(default_factory=CorrectionMetadata)

class ExtractedTable(BaseModel):
    caption: Optional[str] = Field(None, description="The caption of the table.")
    table_data: List[List[str]] = Field(
        ...,
        description="The table content, represented as a list of rows, where each row is a list of strings."
    )
    provenance: Provenance
    correction_metadata: CorrectionMetadata = Field(default_factory=CorrectionMetadata)

class ExtractedFigure(BaseModel):
    caption: str = Field(..., description="The caption of the figure.")
    figure_type: str = Field(..., description="The type of figure (e.g., 'Graph', 'Diagram', 'Image').")
    provenance: Provenance
    correction_metadata: CorrectionMetadata = Field(default_factory=CorrectionMetadata)

class BibliographyItem(BaseModel):
    citation_key: str = Field(..., description="A unique key for the citation, e.g., 'Smith2021'.")
    full_citation: str = Field(..., description="The full, raw text of the bibliographic entry.")

class ArticleExtraction(BaseModel):
    source_filename: str
    title: Optional[str] = None
    authors: List[str] = Field(default_factory=list)
    claims: List[Claim] = Field(default_factory=list)
    pico_elements: Optional[PICO] = None
    quality_scores: List[QualityScore] = Field(default_factory=list)
    tables: List[ExtractedTable] = Field(default_factory=list)
    figures: List[ExtractedFigure] = Field(default_factory=list)
    bibliography: Dict[str, BibliographyItem] = Field(default_factory=dict)