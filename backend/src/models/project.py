"""Project model for organizing content and campaigns."""

import enum
from typing import Optional

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class ProjectStatus(str, enum.Enum):
    """Project status options."""
    
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class Project(Base):
    """Project model for organizing SEO content campaigns."""
    
    # Basic information
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[ProjectStatus] = mapped_column(Enum(ProjectStatus), default=ProjectStatus.ACTIVE)
    
    # Owner relationship
    owner_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False)
    
    # Target configuration
    target_domain: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    target_language: Mapped[str] = mapped_column(String(10), default="ja")
    target_audience: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # SEO settings
    primary_keywords: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array as string
    competitor_urls: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array as string
    
    # Content guidelines
    tone_and_manner: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    brand_voice: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content_guidelines: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Analytics
    articles_count: Mapped[int] = mapped_column(default=0)
    total_views: Mapped[int] = mapped_column(default=0)
    total_conversions: Mapped[int] = mapped_column(default=0)
    
    # Relationships
    owner = relationship("User", back_populates="projects")
    articles = relationship("Article", back_populates="project", cascade="all, delete-orphan")
    keywords = relationship("Keyword", back_populates="project", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name='{self.name}', status='{self.status}')>"