from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, JSON, Text, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from datetime import datetime
import os
import logging
from config import Config

Base = declarative_base()
logger = logging.getLogger(__name__)

# ============ MODELOS DE DATOS ============

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    join_date = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    is_bot = Column(Boolean, default=False)

class Channel(Base):
    __tablename__ = 'channels'
    id = Column(Integer, primary_key=True)
    channel_id = Column(BigInteger, unique=True, nullable=False)
    channel_title = Column(String(255))
    channel_username = Column(String(255))
    owner_id = Column(BigInteger, nullable=False)
    members_count = Column(Integer, default=0)
    is_approved = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    added_date = Column(DateTime, default=datetime.utcnow)
    approved_date = Column(DateTime)
    button_sets = Column(JSON, default=[])
    last_updated = Column(DateTime, default=datetime.utcnow)
    description = Column(Text)

class ButtonSet(Base):
    __tablename__ = 'button_sets'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    min_members = Column(Integer, default=0)
    max_members = Column(Integer, default=1000000)
    description = Column(Text)
    media_file_id = Column(String(500))
    allow_groups = Column(Boolean, default=False)
    pin_message = Column(Boolean, default=False)
    rotate_buttons = Column(Boolean, default=False)
    send_days = Column(JSON, default=[])
    duration_hours = Column(Integer, default=24)
    first_send_time = Column(DateTime)
    extra_buttons = Column(JSON, default=[])
    is_active = Column(Boolean, default=True)
    created_date = Column(DateTime, default=datetime.utcnow)
    created_by = Column(BigInteger)
    last_sent = Column(DateTime)

class AdminSettings(Base):
    __tablename__ = 'admin_settings'
    id = Column(Integer, primary_key=True)
    welcome_text = Column(Text, default="¡Bienvenido al Bot de Botoneras Automáticas!")
    welcome_media = Column(String(500))
    timezone = Column(String(50), default="UTC")
    api_id = Column(String(50))
    api_hash = Column(String(100))
    phone_number = Column(String(20))
    userbot_session = Column(Text)

class BotStats(Base):
    __tablename__ = 'bot_stats'
    id = Column(Integer, primary_key=True)
    total_users = Column(Integer, default=0)
    total_channels = Column(Integer, default=0)
    total_button_sets = Column(Integer, default=0)
    pending_channels = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow)

# ============ CONEXIÓN A BASE DE DATOS ============

engine = None
SessionLocal = None

def init_database():
    """Inicializar base de datos para Replit"""
    global engine, SessionLocal
    
    try:
        db_url = Config.DATABASE_URL
        
        logger.info(f"🔗 Conectando a: {db_url[:50]}...")
        
        # Configurar conexión para Replit DB
        if 'replit.com' in db_url or 'postgres' in db_url:
            # PostgreSQL de Replit
            engine = create_engine(
                db_url,
                echo=False,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True
            )
            logger.info("✅ Conectado a PostgreSQL de Replit")
        else:
            # SQLite local
            engine = create_engine(
                db_url,
                echo=False,
                connect_args={"check_same_thread": False}
            )
            logger.info("✅ Conectado a SQLite local")
        
        # Crear tablas
        Base.metadata.create_all(bind=engine)
        
        # Crear sesión thread-safe
        SessionLocal = scoped_session(sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine
        ))
        
        # Crear configuración por defecto
        session = SessionLocal()
        try:
            settings = session.query(AdminSettings).first()
            if not settings:
                default_settings = AdminSettings()
                session.add(default_settings)
                session.commit()
                logger.info("⚙️ Configuración por defecto creada")
        except Exception as e:
            logger.error(f"Error creando configuración: {e}")
            session.rollback()
        finally:
            session.close()
        
        logger.info("💾 Base de datos inicializada correctamente")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error inicializando base de datos: {e}")
        raise

def get_session():
    """Obtener sesión de base de datos"""
    if not SessionLocal:
        init_database()
    return SessionLocal()
