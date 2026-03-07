from sqlalchemy import Column, Integer, String, Float, ForeignKey, JSON  # type: ignore[import-not-found]
from sqlalchemy.orm import relationship  # type: ignore[import-not-found]
from geoalchemy2 import Geometry  # type: ignore[import-not-found]
from app.database import Base  # type: ignore[import-not-found]

class Node(Base):
    __tablename__ = "nodes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)
    system = Column(String(50), nullable=False, index=True)
    location = Column(Geometry('POINT', srid=4326), nullable=False)
    properties = Column(JSON, default={})

    # Relationships
    outgoing_connections = relationship("Connection", foreign_keys="Connection.source_node_id", back_populates="source_node")
    incoming_connections = relationship("Connection", foreign_keys="Connection.target_node_id", back_populates="target_node")

class Connection(Base):
    __tablename__ = "connections"

    id = Column(Integer, primary_key=True, index=True)
    source_node_id = Column(Integer, ForeignKey("nodes.id"))
    target_node_id = Column(Integer, ForeignKey("nodes.id"))
    type = Column(String(50), nullable=False)
    system = Column(String(50), nullable=False, index=True)
    path = Column(Geometry('LINESTRING', srid=4326), nullable=True)
    intensity = Column(Float, default=1.0)
    properties = Column(JSON, default={})

    # Relationships
    source_node = relationship("Node", foreign_keys=[source_node_id], back_populates="outgoing_connections")
    target_node = relationship("Node", foreign_keys=[target_node_id], back_populates="incoming_connections")
