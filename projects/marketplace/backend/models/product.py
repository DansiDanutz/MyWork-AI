"""
Product and ProductVersion models.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Text, Numeric, Integer, BigInteger, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, TimestampMixin, generate_uuid


class Product(Base, TimestampMixin):
    """Product listing in the marketplace."""

    __tablename__ = "products"

    # Primary key
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid
    )

    # Seller relationship
    seller_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Basic info
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(
        String(200),
        unique=True,
        nullable=False,
        index=True
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    short_description: Mapped[Optional[str]] = mapped_column(String(500))

    # Categorization
    category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )
    subcategory: Mapped[Optional[str]] = mapped_column(String(50))
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)

    # Pricing
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    license_type: Mapped[str] = mapped_column(
        String(20),
        default="standard",  # standard, extended, enterprise
        nullable=False
    )

    # Technical details
    tech_stack: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    framework: Mapped[Optional[str]] = mapped_column(String(50))
    requirements: Mapped[Optional[str]] = mapped_column(Text)

    # Media
    preview_images: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    demo_url: Mapped[Optional[str]] = mapped_column(String(255))
    documentation_url: Mapped[Optional[str]] = mapped_column(String(255))

    # Files
    package_url: Mapped[Optional[str]] = mapped_column(Text)  # R2/S3 URL
    package_size_bytes: Mapped[Optional[int]] = mapped_column(BigInteger)

    # Stats (denormalized for performance)
    views: Mapped[int] = mapped_column(Integer, default=0)
    sales: Mapped[int] = mapped_column(Integer, default=0)
    rating_average: Mapped[float] = mapped_column(Numeric(3, 2), default=0.00)
    rating_count: Mapped[int] = mapped_column(Integer, default=0)

    # Status
    status: Mapped[str] = mapped_column(
        String(20),
        default="draft",  # draft, pending, active, suspended, archived
        nullable=False,
        index=True
    )

    # Featured
    featured: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    featured_until: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )

    # Version
    version: Mapped[str] = mapped_column(String(20), default="1.0.0")
    last_updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True)
    )

    # Relationships
    seller: Mapped["User"] = relationship(
        "User",
        back_populates="products",
        foreign_keys=[seller_id]
    )
    versions: Mapped[List["ProductVersion"]] = relationship(
        "ProductVersion",
        back_populates="product",
        cascade="all, delete-orphan"
    )
    orders: Mapped[List["Order"]] = relationship(
        "Order",
        back_populates="product"
    )
    reviews: Mapped[List["Review"]] = relationship(
        "Review",
        back_populates="product"
    )

    def __repr__(self) -> str:
        return f"<Product {self.title}>"

    @property
    def is_active(self) -> bool:
        """Check if product is active and visible."""
        return self.status == "active"

    @property
    def is_featured(self) -> bool:
        """Check if product is currently featured."""
        if not self.featured:
            return False
        if self.featured_until:
            return self.featured_until > datetime.utcnow()
        return True


class ProductVersion(Base, TimestampMixin):
    """Version history for products."""

    __tablename__ = "product_versions"

    # Primary key
    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=generate_uuid
    )

    # Product relationship
    product_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Version info
    version: Mapped[str] = mapped_column(String(20), nullable=False)
    changelog: Mapped[Optional[str]] = mapped_column(Text)

    # Files
    package_url: Mapped[str] = mapped_column(Text, nullable=False)
    package_size_bytes: Mapped[Optional[int]] = mapped_column(BigInteger)

    # Relationships
    product: Mapped["Product"] = relationship(
        "Product",
        back_populates="versions"
    )

    def __repr__(self) -> str:
        return f"<ProductVersion {self.product_id} v{self.version}>"


# Categories constant
PRODUCT_CATEGORIES = [
    "saas-starters",
    "api-services",
    "automation",
    "mobile-apps",
    "full-applications",
    "components",
    "templates",
    "tools",
]

# License types
LICENSE_TYPES = {
    "standard": {
        "name": "Standard License",
        "description": "Single project use",
        "multiplier": 1.0,
    },
    "extended": {
        "name": "Extended License",
        "description": "Multiple projects, can modify",
        "multiplier": 2.5,
    },
    "enterprise": {
        "name": "Enterprise License",
        "description": "Unlimited use, white-label allowed",
        "multiplier": 5.0,
    },
}


# Import at bottom to avoid circular imports
from models.user import User
from models.order import Order
from models.review import Review
