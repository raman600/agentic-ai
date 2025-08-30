from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy import create_engine


Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password_hash = Column(String)
    created_at = Column(DateTime, default=func.now())
    resumes = relationship("Resume", back_populates="user")

class Resume(Base):
    __tablename__ = "resumes"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    file_name = Column(String)
    raw_text = Column(Text)
    extracted_json = Column(Text)
    created_at = Column(DateTime, default=func.now())
    user = relationship("User", back_populates="resumes")
    scores = relationship("Score", back_populates="resume")

class JobDescription(Base):
    __tablename__ = "job_descriptions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    description = Column(Text)
    created_at = Column(DateTime, default=func.now())

class Score(Base):
    __tablename__ = "scores"
    id = Column(Integer, primary_key=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"))
    job_id = Column(Integer, ForeignKey("job_descriptions.id"))
    score = Column(Integer)
    feedback = Column(Text)
    recommendations = Column(Text)
    created_at = Column(DateTime, default=func.now())
    resume = relationship("Resume", back_populates="scores")

def get_user_resumes(user_id):
    session = SessionLocal()
    resumes = session.query(Resume).filter_by(user_id=user_id).all()
    return resumes

def get_user_job_descriptions(user_id):
    session = SessionLocal()
    jds = session.query(JobDescription).filter_by(user_id=user_id).all()
    return jds

def get_scores_for_resume(resume_id):
    session = SessionLocal()
    scores = session.query(Score).filter_by(resume_id=resume_id).all()
    return scores

# Setup engine
#engine = create_engine("sqlite:///resume_analyzer.db")

engine = create_engine(
    "sqlite:///resume_analyzer.db",
    pool_size=20,        # Increased from default 5
    max_overflow=30,     # Increased from default 10  
    pool_timeout=60,     # Increased timeout from 30s
    pool_recycle=3600,   # Recycle connections every hour
    pool_pre_ping=True   # Verify connections before use
)

Base.metadata.create_all(engine)

SessionLocal = sessionmaker(bind=engine)
