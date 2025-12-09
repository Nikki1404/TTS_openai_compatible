api/benchmark.py-

from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from sqlalchemy.orm import Session
import pandas as pd
import io
from typing import List
from database import SessionLocal
from schemas import FileUploadResponse
import json
from crud import persist_dashboard_entries
from auth import get_current_active_user
from models import User

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post(
    "/upload", 
    response_model=FileUploadResponse,
    summary="Upload benchmark Excel file",
    description="Upload and process an Excel file containing ASR benchmark data",
    response_description="Processed benchmark data ready for analysis",
    responses={
        200: {"description": "File processed successfully"},
        400: {"description": "Invalid file format or missing required columns"},
        500: {"description": "Server error during file processing"}
    },
    tags=["Benchmarks"]
)
async def upload_benchmark_file(
    file: UploadFile = File(
        ..., 
        description="Excel file (.xlsx or .xls) containing benchmark data",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
):
    """
    Upload and process an Excel file containing ASR benchmark data.
    
    **Required Excel columns:**
    - Audio File Name: Name of the audio file tested
    - Audio Length: Duration of audio in seconds
    - Model: Name of the ASR model used
    - Ground_truth: Correct transcription text
    - Transcription: Model's transcription output
    - WER Score: Word Error Rate as a decimal (0.0 to 1.0)
    - Inference time (in sec): Processing time in seconds
    
    **File Requirements:**
    - Format: Excel (.xlsx or .xls)
    - Size: Maximum 50MB
    - Structure: First row must contain column headers
    
    **Returns:**
    - Processed data array ready for dashboard analysis
    - Summary message with processing statistics
    
    **Errors:**
    - 400: Invalid file format or missing required columns
    - 400: Invalid data types in rows
    - 500: Server processing error
    """
    db: Session = next(get_db())
    current_user: User = await get_current_active_user()
    # Validate file type
    if not file.filename or not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(status_code=400, detail="File must be an Excel file (.xlsx or .xls)")
    
    try:
        # Read the uploaded file
        contents = await file.read()
        
        # Parse Excel file using pandas
        df = pd.read_excel(io.BytesIO(contents))
        
        # Validate required columns
        required_columns = [
            'Audio File Name', 'Audio Length', 'Model', 
            'Ground_truth', 'Transcription', 'WER Score', 
            'Inference time (in sec)'
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required columns: {', '.join(missing_columns)}"
            )
        
        # Convert DataFrame to list of dictionaries
        data = df.to_dict('records')
        
        # Clean and validate data
        processed_data = []
        for i, row in enumerate(data):
            try:
                processed_row = {
                    'Audio File Name': str(row.get('Audio File Name', '')),
                    'Audio Length': float(row.get('Audio Length', 0)),
                    'Model': str(row.get('Model', '')),
                    'Ground_truth': str(row.get('Ground_truth', '')),
                    'Transcription': str(row.get('Transcription', '')),
                    'WER Score': float(row.get('WER Score', 0)),
                    'Inference time (in sec)': float(row.get('Inference time (in sec)', 0))
                }
                processed_data.append(processed_row)
            except (ValueError, TypeError) as e:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid data in row {i+2}: {str(e)}"
                )
        
        if not processed_data:
            raise HTTPException(status_code=400, detail="No valid data found in the file")
        
        persist_dashboard_entries(db, processed_data, current_user.id)
        
        return FileUploadResponse(
            data=processed_data,
            message=f"Successfully processed {len(processed_data)} rows from {file.filename}"
        )
        
    except pd.errors.EmptyDataError:
        raise HTTPException(status_code=400, detail="The uploaded file is empty")
    except pd.errors.ParserError as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse the Excel file: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while processing the file: {str(e)}")
    finally:
        await file.close()

  while using this code to upload xlsx file in swgger ui getting this 
INFO:     127.0.0.1:51106 - "POST /api/benchmarks/upload HTTP/1.1" 500 Internal Server Error
ERROR:    Exception in ASGI application
Traceback (most recent call last):
  File "C:\Users\re_nikitav\Desktop\asr_benchmark_frontend\backend\env\Lib\site-packages\uvicorn\protocols\http\httptools_impl.py", line 409, in run_asgi
    result = await app(  # type: ignore[func-returns-value]
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        self.scope, self.receive, self.send
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "C:\Users\re_nikitav\Desktop\asr_benchmark_frontend\backend\env\Lib\site-packages\uvicorn\middleware\proxy_headers.py", line 60, in __call__
    return await self.app(scope, receive, send)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\re_nikitav\Desktop\asr_benchmark_frontend\backend\env\Lib\site-packages\fastapi\applications.py", line 1139, in __call__
    await super().__call__(scope, receive, send)
  File "C:\Users\re_nikitav\Desktop\asr_benchmark_frontend\backend\env\Lib\site-packages\starlette\applications.py", line 107, in __call__
    await self.middleware_stack(scope, receive, send)
  File "C:\Users\re_nikitav\Desktop\asr_benchmark_frontend\backend\env\Lib\site-packages\starlette\middleware\errors.py", line 186, in __call__
    raise exc
  File "C:\Users\re_nikitav\Desktop\asr_benchmark_frontend\backend\env\Lib\site-packages\starlette\middleware\errors.py", line 164, in __call__
    await self.app(scope, receive, _send)
  File "C:\Users\re_nikitav\Desktop\asr_benchmark_frontend\backend\env\Lib\site-packages\starlette\middleware\cors.py", line 93, in __call__
    await self.simple_response(scope, receive, send, request_headers=headers)
  File "C:\Users\re_nikitav\Desktop\asr_benchmark_frontend\backend\env\Lib\site-packages\starlette\middleware\cors.py", line 144, in simple_response
    await self.app(scope, receive, send)
  File "C:\Users\re_nikitav\Desktop\asr_benchmark_frontend\backend\env\Lib\site-packages\starlette\middleware\exceptions.py", line 63, in __call__
    await wrap_app_handling_exceptions(self.app, conn)(scope, receive, send)
  File "C:\Users\re_nikitav\Desktop\asr_benchmark_frontend\backend\env\Lib\site-packages\starlette\_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "C:\Users\re_nikitav\Desktop\asr_benchmark_frontend\backend\env\Lib\site-packages\starlette\_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "C:\Users\re_nikitav\Desktop\asr_benchmark_frontend\backend\env\Lib\site-packages\fastapi\middleware\asyncexitstack.py", line 18, in __call__
    await self.app(scope, receive, send)
  File "C:\Users\re_nikitav\Desktop\asr_benchmark_frontend\backend\env\Lib\site-packages\starlette\routing.py", line 716, in __call__
    await self.middleware_stack(scope, receive, send)
  File "C:\Users\re_nikitav\Desktop\asr_benchmark_frontend\backend\env\Lib\site-packages\starlette\routing.py", line 736, in app
    await route.handle(scope, receive, send)
  File "C:\Users\re_nikitav\Desktop\asr_benchmark_frontend\backend\env\Lib\site-packages\starlette\routing.py", line 290, in handle
    await self.app(scope, receive, send)
  File "C:\Users\re_nikitav\Desktop\asr_benchmark_frontend\backend\env\Lib\site-packages\fastapi\routing.py", line 119, in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
  File "C:\Users\re_nikitav\Desktop\asr_benchmark_frontend\backend\env\Lib\site-packages\starlette\_exception_handler.py", line 53, in wrapped_app
    raise exc
  File "C:\Users\re_nikitav\Desktop\asr_benchmark_frontend\backend\env\Lib\site-packages\starlette\_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File "C:\Users\re_nikitav\Desktop\asr_benchmark_frontend\backend\env\Lib\site-packages\fastapi\routing.py", line 105, in app
    response = await f(request)
               ^^^^^^^^^^^^^^^^
  File "C:\Users\re_nikitav\Desktop\asr_benchmark_frontend\backend\env\Lib\site-packages\fastapi\routing.py", line 385, in app
    raw_response = await run_endpoint_function(
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ...<3 lines>...
    )
    ^
  File "C:\Users\re_nikitav\Desktop\asr_benchmark_frontend\backend\env\Lib\site-packages\fastapi\routing.py", line 284, in run_endpoint_function
    return await dependant.call(**values)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\re_nikitav\Desktop\asr_benchmark_backend\api\benchmarks.py", line 69, in upload_benchmark_file
    current_user: User = await get_current_active_user()
                               ~~~~~~~~~~~~~~~~~~~~~~~^^
  File "C:\Users\re_nikitav\Desktop\asr_benchmark_backend\auth.py", line 120, in get_current_active_user       
    if current_user.status != UserStatus.ACTIVE:
       ^^^^^^^^^^^^^^^^^^^
AttributeError: 'Depends' object has no attribute 'status'



main.py-
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn
import os
from datetime import datetime
from dotenv import load_dotenv

from database import engine, SessionLocal, Base
from api import posts, benchmarks, ai_services
import seed_data

# Load environment variables
load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="ASR Benchmark Hub API",
    description="""
    ## ASR Benchmark Hub Backend API
    
    A comprehensive REST API for managing ASR (Automatic Speech Recognition) benchmark data, 
    blog posts, and AI-powered analysis services.
    
    ### Features
    - **Blog Management**: Create, read, and manage ASR benchmark blog posts
    - **File Processing**: Upload and process Excel benchmark data files
    - **AI Services**: Powered by Google Gemini AI for content generation and analysis
    - **Data Analysis**: Comprehensive benchmark statistics and model comparisons
    
    ### API Categories
    - **Blog Posts**: Manage benchmark reports and analysis articles
    - **Benchmarks**: Upload and process ASR benchmark data files
    - **AI Services**: Generate summaries, reports, and perform error analysis
    
    ### Authentication
    AI services require a valid Google Gemini API key configured in the environment.
    
    ### Data Formats
    - Blog posts support rich HTML content with embedded benchmark data
    - Excel uploads must follow the specified column format
    - All responses follow consistent JSON schemas
    """,
    version="1.0.0",
    contact={
        "name": "ASR Benchmark Hub",
        "url": "https://github.com/yourusername/asr-benchmark-hub"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    },
    openapi_tags=[
        {
            "name": "Blog Posts",
            "description": "Operations for managing ASR benchmark blog posts and reports"
        },
        {
            "name": "Benchmarks", 
            "description": "File upload and processing operations for benchmark data"
        },
        {
            "name": "AI Services",
            "description": "AI-powered content generation and analysis services using Google Gemini"
        }
    ]
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Include API routers
from api import users
app.include_router(posts.router, prefix="/api/posts", tags=["posts"])
app.include_router(benchmarks.router, prefix="/api/benchmarks", tags=["benchmarks"])
app.include_router(ai_services.router, prefix="/api/ai", tags=["ai"])
app.include_router(users.router, prefix="/api/auth", tags=["authentication", "users"])

@app.on_event("startup")
async def startup_event():
    """Seed the database with initial data if it's empty"""
    db = SessionLocal()
    try:
        seed_data.seed_database(db)
    finally:
        db.close()

@app.get(
    "/",
    summary="API Root",
    description="Get basic API information and status",
    response_description="API welcome message and version info",
    tags=["System"]
)
async def root():
    """
    API root endpoint providing basic information about the ASR Benchmark Hub API.
    
    Returns:
    - API name and version
    - Basic status information
    """
    return {
        "message": "ASR Benchmark Hub API", 
        "version": "1.0.0",
        "description": "Backend API for ASR benchmark data management and AI analysis",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

@app.get(
    "/health",
    summary="Health Check",
    description="Check API health and database connectivity", 
    response_description="System health status",
    tags=["System"]
)
async def health_check():
    """
    Health check endpoint for monitoring and uptime verification.
    
    Returns:
    - System health status
    - API availability confirmation
    
    Use this endpoint for:
    - Load balancer health checks
    - Monitoring system integration
    - Service availability verification
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

api/ai_services.py-
from fastapi import APIRouter, HTTPException
import google.generativeai as genai
import os
from dotenv import load_dotenv
from schemas import (
    SummarizeRequest, SummarizeResponse, 
    BlogGenerationData, BlogPostOutput,
    AnalyzeErrorsRequest, AnalysisResult, TranscriptionError,
    CompareModelsRequest, HeadToHeadAnalysis
)
import json
import re

# Load environment variables
load_dotenv()

router = APIRouter()

# Configure Google Gemini API
api_key = os.getenv("API_KEY")
if not api_key:
    raise ValueError("API_KEY environment variable is required")

genai.configure(api_key=api_key)

# Initialize the model
model = genai.GenerativeModel('gemini-2.5-pro')

@router.post(
    "/summarize", 
    response_model=SummarizeResponse,
    summary="Generate content summary",
    description="Generate a concise AI-powered summary of the provided text content",
    response_description="Concise summary of the input content",
    responses={
        200: {"description": "Summary generated successfully"},
        500: {"description": "AI service error or API key issues"}
    },
    tags=["AI Services"]
)
async def summarize_content(request: SummarizeRequest):
    """
    Generate a concise summary of text content using Google Gemini AI.
    
    **Input:**
    - **content**: Text content to summarize (any length)
    
    **AI Processing:**
    - Uses Google Gemini 1.5 Flash model
    - Generates 2-3 sentence summaries
    - Focuses on key insights and main findings
    - Optimized for technical content
    
    **Output:**
    - Concise summary highlighting main points
    - Professional tone suitable for technical audiences
    
    **Error Handling:**
    - 500: AI service unavailable or API key invalid
    - 500: Content processing errors
    
    **Note:** Requires valid GEMINI_API_KEY in environment variables.
    """
    try:
        prompt = f"""
        Please provide a concise summary of the following content in 2-3 sentences:
        
        {request.content}
        
        Focus on the key insights and main findings.
        """
        
        response = model.generate_content(prompt)
        
        if not response.text:
            raise HTTPException(status_code=500, detail="Failed to generate summary")
        
        return SummarizeResponse(summary=response.text.strip())
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")

@router.post(
    "/generate-report", 
    response_model=BlogPostOutput,
    summary="Generate benchmark report",
    description="Generate a complete blog post from ASR benchmark statistics using AI",
    response_description="Complete blog post with title, excerpt, and HTML content",
    responses={
        200: {"description": "Blog post generated successfully"},
        500: {"description": "AI service error during blog generation"}
    },
    tags=["AI Services"]
)
async def generate_blog_post(data: BlogGenerationData):
    """
    Generate a comprehensive blog post from ASR benchmark data using AI.
    
    **Input Data Structure:**
    - **summaryStats**: Overall statistics (totalFiles, avgWer, avgInferenceTime)
    - **modelPerformance**: Per-model performance metrics array
    - **fileName**: Source file name for context
    
    **AI Generation Features:**
    - Professional technical writing style
    - Comprehensive analysis and insights
    - HTML-formatted content with proper structure
    - Model performance comparisons
    - Trade-off analysis between accuracy and speed
    
    **Output Components:**
    - **title**: Compelling, descriptive title
    - **excerpt**: 2-3 sentence summary for previews
    - **content**: Full HTML blog content with headings, analysis, and insights
    
    **Content Includes:**
    - Executive summary of results
    - Detailed model performance analysis
    - Comparative insights between models
    - Technical recommendations
    - Visual data presentation suggestions
    
    **Error Handling:**
    - Fallback content generation if AI parsing fails
    - Graceful degradation for incomplete data
    """
    try:
        # Format the data for the prompt
        summary_stats = data.summaryStats
        model_performance = data.modelPerformance
        file_name = data.fileName
        
        prompt = f"""
        Generate a comprehensive blog post about ASR (Automatic Speech Recognition) benchmark results. Use the following data:

        **File Name:** {file_name}
        **Summary Statistics:**
        - Total Files: {summary_stats.get('totalFiles', 0)}
        - Average WER: {summary_stats.get('avgWer', 0)}%
        - Average Inference Time: {summary_stats.get('avgInferenceTime', 0)} seconds

        **Model Performance:**
        {json.dumps(model_performance, indent=2)}

        Please create:
        1. A compelling title
        2. A brief excerpt (2-3 sentences)
        3. Full blog content in HTML format with proper headings and structure

        The blog should be professional, informative, and suitable for a technical audience interested in ASR benchmarks.
        Include analysis of the results, comparisons between models, and insights about performance trade-offs.
        
        Return the response in this exact JSON format:
        {{
            "title": "Your Title Here",
            "excerpt": "Your excerpt here",
            "content": "Your HTML content here"
        }}
        """
        
        response = model.generate_content(prompt)
        
        if not response.text:
            raise HTTPException(status_code=500, detail="Failed to generate blog post")
        
        # Try to parse JSON response
        try:
            # Extract JSON from response text
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return BlogPostOutput(**result)
            else:
                # Fallback if JSON parsing fails
                lines = response.text.strip().split('\n')
                return BlogPostOutput(
                    title=f"ASR Benchmark Analysis: {file_name}",
                    excerpt="Comprehensive analysis of ASR model performance showing detailed metrics and comparisons across different models and datasets.",
                    content=f"<h2>Benchmark Analysis Results</h2><pre>{response.text}</pre>"
                )
        except json.JSONDecodeError:
            # Fallback response
            return BlogPostOutput(
                title=f"ASR Benchmark Analysis: {file_name}",
                excerpt="Detailed performance analysis of ASR models with comprehensive metrics and insights.",
                content=f"<h2>Analysis Results</h2><div>{response.text}</div>"
            )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating blog post: {str(e)}")

@router.post(
    "/analyze-errors", 
    response_model=AnalysisResult,
    summary="Analyze transcription errors",
    description="AI-powered analysis of transcription errors comparing ground truth with model output",
    response_description="Detailed error analysis with categorized transcription mistakes",
    responses={
        200: {"description": "Error analysis completed successfully"},
        500: {"description": "AI service error during analysis"}
    },
    tags=["AI Services"]
)
async def analyze_transcription_errors(request: AnalyzeErrorsRequest):
    """
    Analyze transcription errors using AI-powered text comparison.
    
    **Input:**
    - **ground_truth**: Correct transcription text
    - **transcription**: ASR model output to analyze
    
    **Error Categories:**
    - **Substitution**: Word replaced with incorrect word
    - **Deletion**: Word missing from transcription
    - **Insertion**: Extra word added in transcription
    
    **Analysis Features:**
    - Intelligent text alignment and comparison
    - Context-aware error detection
    - Linguistic pattern recognition
    - Quality assessment summary
    
    **Output:**
    - **summary**: Overall transcription quality assessment
    - **errors**: Array of categorized errors with:
      - Error type classification
      - Relevant ground truth segment
      - Corresponding transcription segment
    
    **Use Cases:**
    - Model performance debugging
    - Training data quality assessment
    - Error pattern identification
    - Transcription accuracy improvement
    
    **AI Processing:**
    - Advanced NLP techniques for alignment
    - Context-sensitive error categorization
    - Detailed linguistic analysis
    """
    try:
        prompt = f"""
        Analyze the differences between these two texts and categorize the errors:

        **Ground Truth:** {request.ground_truth}
        **Transcription:** {request.transcription}

        Please:
        1. Provide a brief summary of the transcription quality
        2. Identify and categorize errors as:
           - Substitution: word replaced with another word
           - Deletion: word missing from transcription
           - Insertion: extra word in transcription

        Return the response in this exact JSON format:
        {{
            "summary": "Brief analysis of transcription quality and main issues",
            "errors": [
                {{
                    "type": "Substitution|Deletion|Insertion",
                    "ground_truth_segment": "relevant ground truth text",
                    "transcription_segment": "corresponding transcription text"
                }}
            ]
        }}
        """
        
        response = model.generate_content(prompt)
        
        if not response.text:
            raise HTTPException(status_code=500, detail="Failed to analyze errors")
        
        # Parse JSON response
        try:
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                # Validate and create TranscriptionError objects
                errors = []
                for error in result.get('errors', []):
                    errors.append(TranscriptionError(
                        type=error.get('type', 'Substitution'),
                        ground_truth_segment=error.get('ground_truth_segment', ''),
                        transcription_segment=error.get('transcription_segment', '')
                    ))
                
                return AnalysisResult(
                    summary=result.get('summary', 'Analysis completed'),
                    errors=errors
                )
        except json.JSONDecodeError:
            pass
        
        # Fallback response
        return AnalysisResult(
            summary=f"Transcription analysis completed. Response: {response.text[:200]}...",
            errors=[]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing errors: {str(e)}")

@router.post(
    "/compare-models", 
    response_model=HeadToHeadAnalysis,
    summary="Compare ASR models",
    description="AI-powered head-to-head comparison analysis between two ASR models",
    response_description="Comprehensive comparison analysis with winner determination and insights",
    responses={
        200: {"description": "Model comparison analysis completed successfully"},
        500: {"description": "AI service error during comparison"}
    },
    tags=["AI Services"]
)
async def compare_models(request: CompareModelsRequest):
    """
    Generate a comprehensive head-to-head comparison between two ASR models.
    
    **Input Structure:**
    - **model_a**: Object with name and benchmark data array
    - **model_b**: Object with name and benchmark data array
    
    **Data Analysis:**
    - Statistical performance comparison
    - Accuracy metrics evaluation (WER scores)
    - Speed analysis (inference times)
    - Consistency assessment across test cases
    
    **Comparison Dimensions:**
    - **Accuracy**: WER scores, transcription quality
    - **Speed**: Inference time, real-time factor
    - **Consistency**: Performance variance
    - **Use Case Suitability**: Optimal application scenarios
    
    **Output Analysis:**
    - **winner**: Overall best performing model
    - **summary**: Executive summary of key findings
    - **accuracyAnalysis**: Detailed accuracy comparison
    - **speedAnalysis**: Performance and latency analysis
    - **tradeOffs**: Discussion of trade-offs and recommendations
    
    **AI Insights:**
    - Statistical significance testing
    - Performance trend analysis
    - Context-aware recommendations
    - Use case optimization suggestions
    
    **Applications:**
    - Model selection guidance
    - Performance optimization
    - Benchmarking reports
    - Technical decision support
    """
    try:
        model_a = request.model_a
        model_b = request.model_b
        
        prompt = f"""
        Perform a detailed head-to-head comparison between two ASR models:

        **Model A: {model_a.get('name', 'Model A')}**
        Data: {json.dumps(model_a.get('data', [])[:5], indent=2)}  # First 5 entries for analysis

        **Model B: {model_b.get('name', 'Model B')}**
        Data: {json.dumps(model_b.get('data', [])[:5], indent=2)}  # First 5 entries for analysis

        Please analyze and provide:
        1. Overall winner based on performance metrics
        2. Summary of key differences
        3. Detailed accuracy analysis
        4. Speed/inference time analysis
        5. Trade-offs between the models

        Return the response in this exact JSON format:
        {{
            "winner": "Model name that performs better overall",
            "summary": "Brief summary of the comparison results",
            "accuracyAnalysis": "Detailed analysis of accuracy differences",
            "speedAnalysis": "Analysis of inference speed differences", 
            "tradeOffs": "Discussion of trade-offs between the models"
        }}
        """
        
        response = model.generate_content(prompt)
        
        if not response.text:
            raise HTTPException(status_code=500, detail="Failed to generate comparison")
        
        # Parse JSON response
        try:
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return HeadToHeadAnalysis(**result)
        except json.JSONDecodeError:
            pass
        
        # Fallback response
        return HeadToHeadAnalysis(
            winner=model_a.get('name', 'Model A'),
            summary="Comparison analysis completed successfully.",
            accuracyAnalysis=f"Analysis results: {response.text[:300]}...",
            speedAnalysis="Speed comparison analysis provided.",
            tradeOffs="Trade-off analysis between the models provided."
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing models: {str(e)}")

api/users.py-"""
User management and authentication API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, timedelta
import secrets
import string

from database import get_db
from models import User, UserRole, UserStatus, BlogPost, AuditLog
from schemas import (
    UserCreate, UserResponse, UserLogin, TokenResponse, UserUpdate,
    UserAdminUpdate, RefreshTokenRequest, PasswordResetRequest, 
    PasswordResetConfirm, AuditLogResponse, SystemStatsResponse
)
from auth import (
    AuthService, get_current_user, get_current_active_user, 
    require_admin, require_role, log_user_action
)

router = APIRouter()

def generate_verification_token() -> str:
    """Generate a secure verification token"""
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Register a new user account"""
    
    # Validate password confirmation
    if user_data.password != user_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    # Check if username already exists
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    # Create new user
    hashed_password = AuthService.get_password_hash(user_data.password)
    verification_token = generate_verification_token()
    
    # First user becomes admin
    user_count = db.query(User).count()
    initial_role = UserRole.ADMIN if user_count == 0 else UserRole.VIEWER
    
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        bio=user_data.bio,
        hashed_password=hashed_password,
        role=initial_role,
        email_verification_token=verification_token,
        preferences={"theme": "light", "email_notifications": True}
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Log registration
    log_user_action(
        db=db,
        user=db_user,
        action="user_registered",
        resource_type="user",
        resource_id=db_user.id,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return db_user

@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """Authenticate user and return tokens"""
    
    # Find user by username or email
    user = db.query(User).filter(
        (User.username == login_data.username_or_email) | 
        (User.email == login_data.username_or_email)
    ).first()
    
    if not user or not AuthService.verify_password(login_data.password, user.hashed_password):
        log_user_action(
            db=db,
            user=None,
            action="login_failed",
            details={"username_or_email": login_data.username_or_email},
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent")
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password"
        )
    
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive. Please contact administrator."
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create tokens
    access_token = AuthService.create_access_token(data={"sub": user.id})
    refresh_token = AuthService.create_refresh_token(data={"sub": user.id})
    
    # Log successful login
    log_user_action(
        db=db,
        user=user,
        action="login_success",
        resource_type="user",
        resource_id=user.id,
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=30 * 60,  # 30 minutes
        user=UserResponse.from_orm(user)
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    token_data: RefreshTokenRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """Refresh access token using refresh token"""
    
    payload = AuthService.decode_token(token_data.refresh_token)
    
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    
    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user or user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user"
        )
    
    # Create new tokens
    access_token = AuthService.create_access_token(data={"sub": user.id})
    new_refresh_token = AuthService.create_refresh_token(data={"sub": user.id})
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=30 * 60,
        user=UserResponse.from_orm(user)
    )

@router.get("/profile", response_model=UserResponse)
async def get_profile(current_user: User = Depends(get_current_active_user)):
    """Get current user profile"""
    return current_user

@router.put("/profile", response_model=UserResponse)
async def update_profile(
    user_data: UserUpdate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user profile"""
    
    for field, value in user_data.dict(exclude_unset=True).items():
        setattr(current_user, field, value)
    
    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)
    
    # Log profile update
    log_user_action(
        db=db,
        user=current_user,
        action="profile_updated",
        resource_type="user",
        resource_id=current_user.id,
        details={"updated_fields": list(user_data.dict(exclude_unset=True).keys())},
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return current_user

# ===== ADMIN ENDPOINTS =====

@router.get("/users", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    role: Optional[UserRole] = None,
    status: Optional[UserStatus] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """List all users (Admin only)"""
    
    query = db.query(User)
    
    if role:
        query = query.filter(User.role == role)
    if status:
        query = query.filter(User.status == status)
    
    users = query.offset(skip).limit(limit).all()
    return users

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get specific user (Admin only)"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserAdminUpdate,
    request: Request,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update user (Admin only)"""
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    for field, value in user_data.dict(exclude_unset=True).items():
        setattr(user, field, value)
    
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    # Log admin action
    log_user_action(
        db=db,
        user=current_user,
        action="user_updated_by_admin",
        resource_type="user",
        resource_id=user.id,
        details={"updated_fields": list(user_data.dict(exclude_unset=True).keys())},
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    return user

@router.get("/audit-logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    skip: int = 0,
    limit: int = 100,
    action: Optional[str] = None,
    user_id: Optional[str] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get audit logs (Admin only)"""
    
    query = db.query(AuditLog).options(joinedload(AuditLog.user))
    
    if action:
        query = query.filter(AuditLog.action.contains(action))
    if user_id:
        query = query.filter(AuditLog.user_id == user_id)
    
    logs = query.order_by(desc(AuditLog.timestamp)).offset(skip).limit(limit).all()
    return logs

@router.get("/stats", response_model=SystemStatsResponse)
async def get_system_stats(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Get system statistics (Admin only)"""
    
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.status == UserStatus.ACTIVE).count()
    total_posts = db.query(BlogPost).count()
    
    # Get recent activities
    recent_activities = db.query(AuditLog).options(joinedload(AuditLog.user))\
                          .order_by(desc(AuditLog.timestamp))\
                          .limit(10).all()
    
    # User growth over last 30 days
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    user_growth = db.query(
        func.date(User.created_at).label('date'),
        func.count(User.id).label('count')
    ).filter(User.created_at >= thirty_days_ago)\
     .group_by(func.date(User.created_at))\
     .all()
    
    user_growth_data = [{"date": str(date), "count": count} for date, count in user_growth]
    
    return SystemStatsResponse(
        total_users=total_users,
        active_users=active_users,
        total_posts=total_posts,
        total_uploads=0,  # TODO: Implement upload tracking
        recent_activities=[AuditLogResponse.from_orm(log) for log in recent_activities],
        user_growth=user_growth_data,
        popular_models=[]  # TODO: Implement model popularity tracking
    )

api/postes.py-
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import SessionLocal
from schemas import BlogPostCreate, BlogPostResponse
import crud

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get(
    "/", 
    response_model=List[BlogPostResponse],
    summary="Get all blog posts",
    description="Retrieve a paginated list of all blog posts with their benchmark data",
    response_description="List of blog posts with pagination support",
    tags=["Blog Posts"]
)
async def get_posts(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """
    Retrieve all blog posts from the database.
    
    - **skip**: Number of posts to skip (for pagination)
    - **limit**: Maximum number of posts to return (default: 100, max: 100)
    
    Returns a list of blog posts sorted by creation date (newest first).
    Each post includes benchmark data and model performance metrics if available.
    """
    posts = crud.get_blog_posts(db, skip=skip, limit=limit)
    
    # Convert JSON fields back to proper format for frontend
    response_posts = []
    for post in posts:
        post_dict = {
            "id": post.id,
            "title": post.title,
            "date": post.date.isoformat() if post.date else None,
            "author": post.author,
            "excerpt": post.excerpt,
            "content": post.content,
            "benchmarkData": post.benchmark_data,
            "modelPerformanceData": post.model_performance_data
        }
        response_posts.append(post_dict)
    
    return response_posts

@router.post(
    "/", 
    response_model=BlogPostResponse,
    status_code=201,
    summary="Create a new blog post",
    description="Create a new blog post with optional benchmark data and model performance metrics",
    response_description="The created blog post with assigned ID and timestamp",
    tags=["Blog Posts"]
)
async def create_post(
    post: BlogPostCreate, 
    db: Session = Depends(get_db)
):
    """
    Create a new blog post in the database.
    
    - **title**: The title of the blog post
    - **author**: Author of the blog post
    - **excerpt**: Brief summary/excerpt of the post
    - **content**: Full HTML content of the blog post
    - **benchmark_data**: Optional array of benchmark results
    - **model_performance_data**: Optional array of model performance metrics
    
    The system automatically assigns a unique ID and timestamp to the post.
    """
    db_post = crud.create_blog_post(db=db, post=post)
    
    # Format response to match frontend expectations
    response = {
        "id": db_post.id,
        "title": db_post.title,
        "date": db_post.date.isoformat() if db_post.date else None,
        "author": db_post.author,
        "excerpt": db_post.excerpt,
        "content": db_post.content,
        "benchmarkData": db_post.benchmark_data,
        "modelPerformanceData": db_post.model_performance_data
    }
    
    return response

@router.get(
    "/{post_id}", 
    response_model=BlogPostResponse,
    summary="Get a specific blog post",
    description="Retrieve a single blog post by its unique identifier",
    response_description="The requested blog post with all associated data",
    responses={
        404: {"description": "Blog post not found"},
        200: {"description": "Blog post retrieved successfully"}
    },
    tags=["Blog Posts"]
)
async def get_post(
    post_id: str, 
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific blog post by its unique ID.
    
    - **post_id**: Unique identifier of the blog post
    
    Returns the complete blog post including:
    - Basic post information (title, author, date, excerpt, content)
    - Associated benchmark data if available
    - Model performance metrics if available
    
    Raises 404 error if the post is not found.
    """
    db_post = crud.get_blog_post(db, post_id=post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Format response to match frontend expectations
    response = {
        "id": db_post.id,
        "title": db_post.title,
        "date": db_post.date.isoformat() if db_post.date else None,
        "author": db_post.author,
        "excerpt": db_post.excerpt,
        "content": db_post.content,
        "benchmarkData": db_post.benchmark_data,
        "modelPerformanceData": db_post.model_performance_data
    }
    
    return response


auth.py-
"""
Authentication and authorization utilities for ASR Benchmark Hub
"""

from jose import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from models import User, UserRole, UserStatus, AuditLog
from database import get_db
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Bearer token security
security = HTTPBearer()

class AuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    @staticmethod
    def create_refresh_token(data: Dict[str, Any]) -> str:
        """Create a JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    @staticmethod
    def decode_token(token: str) -> Dict[str, Any]:
        """Decode and verify a JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get the current authenticated user"""
    token = credentials.credentials
    payload = AuthService.decode_token(token)
    
    # Verify token type
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get the current active user"""
    if current_user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
    return current_user

def require_role(required_role: UserRole):
    """Dependency factory for role-based access control"""
    def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role == UserRole.ADMIN:
            return current_user  # Admins have access to everything
        
        role_hierarchy = {
            UserRole.VIEWER: 0,
            UserRole.EDITOR: 1,
            UserRole.ADMIN: 2
        }
        
        if role_hierarchy.get(current_user.role, 0) < role_hierarchy.get(required_role, 0):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker

def require_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """Require admin role"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

def log_user_action(
    db: Session,
    user: Optional[User],
    action: str,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
):
    """Log user actions for audit trail"""
    audit_log = AuditLog(
        user_id=user.id if user else None,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        ip_address=ip_address,
        user_agent=user_agent
    )
    db.add(audit_log)
    db.commit()

# Optional user dependency (doesn't require authentication)
def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user if authenticated, otherwise return None"""
    if not credentials:
        return None
    
    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None

create_demo_users.py-
"""
Seed script for creating demo users in the database
"""

from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import User, UserRole, UserStatus, Base
from auth import AuthService
from datetime import datetime

# Create database tables
Base.metadata.create_all(bind=engine)

def create_demo_users():
    """Create demo users for testing"""
    db = SessionLocal()
    try:
        # Check if admin user already exists
        existing_admin = db.query(User).filter(User.email == "admin@demo.com").first()
        if existing_admin:
            print("Demo users already exist!")
            return

        # Create demo users
        demo_users = [
            {
                "username": "admin_user",
                "email": "admin@demo.com",
                "password": "password123",
                "full_name": "System Administrator",
                "role": UserRole.ADMIN,
                "bio": "System administrator with full access to all features."
            },
            {
                "username": "editor_user", 
                "email": "editor@demo.com",
                "password": "password123",
                "full_name": "Content Editor",
                "role": UserRole.EDITOR,
                "bio": "Content editor with publish and analysis permissions."
            },
            {
                "username": "viewer_user",
                "email": "viewer@demo.com", 
                "password": "password123",
                "full_name": "Data Viewer",
                "role": UserRole.VIEWER,
                "bio": "Viewer with read-only access to published content."
            }
        ]

        for user_data in demo_users:
            # Truncate password to 72 bytes for bcrypt
            password = user_data["password"][:72]
            hashed_password = AuthService.get_password_hash(password)
            
            db_user = User(
                username=user_data["username"],
                email=user_data["email"],
                full_name=user_data["full_name"],
                bio=user_data["bio"],
                hashed_password=hashed_password,
                role=user_data["role"],
                status=UserStatus.ACTIVE,
                is_email_verified=True,
                created_at=datetime.utcnow(),
                preferences={"theme": "light", "email_notifications": True}
            )
            
            db.add(db_user)

        db.commit()
        print("Demo users created successfully!")
        print("- Admin: admin@demo.com / password123")
        print("- Editor: editor@demo.com / password123") 
        print("- Viewer: viewer@demo.com / password123")

    except Exception as e:
        print(f"Error creating demo users: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_demo_users()

crud.py-from sqlalchemy.orm import Session
from models import BlogPost, BenchmarkResult, DashboardData
from schemas import BlogPostCreate
import json
import uuid
from typing import List, Dict, Union

def create_blog_post(db: Session, post: BlogPostCreate):
    # Convert Pydantic models to dict for JSON storage
    benchmark_data = None
    if post.benchmark_data:
        benchmark_data = [item.model_dump() for item in post.benchmark_data]
    
    model_performance_data = None
    if post.model_performance_data:
        model_performance_data = [item.model_dump() for item in post.model_performance_data]
    
    db_post = BlogPost(
        title=post.title,
        author=post.author,
        excerpt=post.excerpt,
        content=post.content,
        benchmark_data=benchmark_data,
        model_performance_data=model_performance_data
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post

def get_blog_posts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(BlogPost).offset(skip).limit(limit).all()

def get_blog_post(db: Session, post_id: str):
    return db.query(BlogPost).filter(BlogPost.id == post_id).first()

def create_benchmark_result(db: Session, model: str, wer: float, dataset: str):
    db_result = BenchmarkResult(model=model, wer=wer, dataset=dataset)
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return db_result

def get_benchmark_results(db: Session):
    return db.query(BenchmarkResult).all()

def create_dashboard_data(db: Session, data: dict):
    db_data = DashboardData(**data)
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data

def get_dashboard_data(db: Session):
    return db.query(DashboardData).all()

def persist_dashboard_entries(
    db: Session,
    rows: Union[Dict, List[Dict]],
    user_id: str
):
    """
    Universal persistence function:
    - Accepts one dict OR list of dicts.
    - Auto-detects single vs multiple entries.
    - Uses bulk insert for performance.
    - Safe for concurrent writes.
    - Automatically rolls back on error.
    """

    if isinstance(rows, dict):
        rows = [rows]

    entries = []

    try:
        for r in rows:
            entry = DashboardData(
                id=str(uuid.uuid4()),
                audio_file_name=r.get("Audio File Name"),
                audio_length=r.get("Audio Length"),
                model=r.get("Model"),
                ground_truth=r.get("Ground_truth"),
                transcription=r.get("Transcription"),
                wer_score=r.get("WER Score"),
                inference_time=r.get("Inference time (in sec)"),
                created_by=user_id
            )
            entries.append(entry)

        if len(entries) == 1:
            db.add(entries[0])
            db.commit()
            db.refresh(entries[0])
        else:
            db.bulk_save_objects(entries)
            db.commit()

        return entries

    except Exception as e:
        db.rollback()
        raise RuntimeError(f"Failed to persist dashboard entries: {e}")

database.py-
from sqlalchemy import create_engine, Column, String, Float, Integer, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

SQLALCHEMY_DATABASE_URL = "sqlite:///./asr_benchmark.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
helpers.py-
def calculate_statistics(data):
    """Helper function to calculate statistics from dashboard data"""
    if not data:
        return {}
    
    total_files = len(data)
    avg_wer = sum(row.get('WER Score', 0) for row in data) / total_files if total_files > 0 else 0
    avg_inference_time = sum(row.get('Inference time (in sec)', 0) for row in data) / total_files if total_files > 0 else 0
    
    return {
        'totalFiles': total_files,
        'avgWer': round(avg_wer, 4),
        'avgInferenceTime': round(avg_inference_time, 4)
    }

def calculate_model_performance(data):
    """Helper function to calculate per-model performance statistics"""
    if not data:
        return []
    
    models = {}
    for row in data:
        model = row.get('Model', 'Unknown')
        if model not in models:
            models[model] = {'wer_scores': [], 'inference_times': []}
        
        models[model]['wer_scores'].append(row.get('WER Score', 0))
        models[model]['inference_times'].append(row.get('Inference time (in sec)', 0))
    
    model_performance = []
    for model, stats in models.items():
        avg_wer = sum(stats['wer_scores']) / len(stats['wer_scores']) if stats['wer_scores'] else 0
        avg_inference = sum(stats['inference_times']) / len(stats['inference_times']) if stats['inference_times'] else 0
        
        model_performance.append({
            'model': model,
            'avgWer': round(avg_wer, 4),
            'avgInferenceTime': round(avg_inference, 4)
        })
    
    return model_performance
models.py-from sqlalchemy import Column, String, Text, DateTime, Float, Integer, JSON, Boolean, Enum as SQLEnum, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import uuid
import enum
from datetime import datetime

class UserRole(enum.Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"

class UserStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class BlogPost(Base):
    __tablename__ = "blog_posts"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    date = Column(DateTime, default=func.now(), nullable=False)
    author = Column(String, nullable=False)  # Keep for backward compatibility
    author_id = Column(String, ForeignKey("users.id"), nullable=True)  # Link to user
    excerpt = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    status = Column(String, default="published")  # draft, published, archived
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    benchmark_data = Column(JSON, nullable=True)  # Store as JSON
    model_performance_data = Column(JSON, nullable=True)  # Store as JSON
    tags = Column(JSON, nullable=True)  # Post tags for categorization
    views_count = Column(Integer, default=0)  # Track post views
    likes_count = Column(Integer, default=0)  # Track post likes
    
    # Relationships
    author_user = relationship("User", back_populates="blog_posts")

class BenchmarkResult(Base):
    __tablename__ = "benchmark_results"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    model = Column(String, nullable=False)
    wer = Column(Float, nullable=False)
    dataset = Column(String, nullable=False)
    
class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String(100), nullable=True)
    role = Column(SQLEnum(UserRole), default=UserRole.VIEWER, nullable=False)
    status = Column(SQLEnum(UserStatus), default=UserStatus.ACTIVE, nullable=False)
    avatar_url = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_email_verified = Column(Boolean, default=False)
    email_verification_token = Column(String, nullable=True)
    password_reset_token = Column(String, nullable=True)
    password_reset_expires = Column(DateTime(timezone=True), nullable=True)
    preferences = Column(JSON, nullable=True)  # User preferences/settings
    
    # Relationships
    blog_posts = relationship("BlogPost", back_populates="author_user")
    audit_logs = relationship("AuditLog", back_populates="user")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)  # login, create_post, delete_user, etc.
    resource_type = Column(String(50), nullable=True)  # user, post, file, etc.
    resource_id = Column(String, nullable=True)
    details = Column(JSON, nullable=True)  # Additional context
    ip_address = Column(String(45), nullable=True)  # IPv6 support
    user_agent = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")

class DashboardData(Base):
    __tablename__ = "dashboard_data"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    audio_file_name = Column(String, nullable=False)
    audio_length = Column(Float, nullable=False)
    model = Column(String, nullable=False)
    ground_truth = Column(Text, nullable=False)
    transcription = Column(Text, nullable=False)
    wer_score = Column(Float, nullable=False)
    inference_time = Column(Float, nullable=False)
    created_by = Column(String, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    schemas.py-

    from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime
from models import UserRole, UserStatus

# Blog Post schemas
class BenchmarkResultSchema(BaseModel):
    """Individual benchmark result for a model on a specific dataset"""
    model: str = Field(..., description="Name of the ASR model tested", example="Whisper-large")
    wer: float = Field(..., description="Word Error Rate as a decimal (0.0 = perfect, 1.0 = completely wrong)", ge=0.0, le=1.0, example=0.123)
    dataset: str = Field(..., description="Name of the dataset used for testing", example="LibriSpeech-clean")

class ModelPerformanceDataSchema(BaseModel):
    """Aggregated performance metrics for a model across multiple tests"""
    model: str = Field(..., description="Name of the ASR model", example="Whisper-large")
    avgWer: float = Field(..., description="Average Word Error Rate across all tests", ge=0.0, le=1.0, example=0.145)

class BlogPostBase(BaseModel):
    """Base schema for blog post data"""
    title: str = Field(..., description="Blog post title", min_length=5, max_length=200, example="Whisper vs Traditional STT: Comprehensive Benchmark Analysis")
    author: str = Field(..., description="Author name", min_length=2, max_length=100, example="ASR Research Team")
    excerpt: str = Field(..., description="Brief summary/excerpt of the blog post", min_length=10, max_length=500, example="An in-depth comparison of OpenAI's Whisper model against traditional speech-to-text solutions...")
    content: str = Field(..., description="Full HTML content of the blog post", min_length=50, example="<h2>Executive Summary</h2><p>This analysis examines...</p>")
    benchmark_data: Optional[List[BenchmarkResultSchema]] = Field(None, description="Array of benchmark results associated with this post")
    model_performance_data: Optional[List[ModelPerformanceDataSchema]] = Field(None, description="Array of model performance summaries")

class BlogPostCreate(BlogPostBase):
    """Schema for creating a new blog post"""
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Whisper vs Traditional STT: Comprehensive Benchmark Analysis",
                "author": "ASR Research Team",
                "excerpt": "An in-depth comparison of OpenAI's Whisper model against traditional speech-to-text solutions, analyzing accuracy, speed, and resource consumption.",
                "content": "<h2>Executive Summary</h2><p>This comprehensive analysis examines the performance characteristics of OpenAI's Whisper model compared to traditional speech-to-text solutions.</p>",
                "benchmark_data": [
                    {"model": "Whisper-large", "wer": 0.123, "dataset": "LibriSpeech-clean"},
                    {"model": "Traditional-STT", "wer": 0.187, "dataset": "LibriSpeech-clean"}
                ],
                "model_performance_data": [
                    {"model": "Whisper-large", "avgWer": 0.145},
                    {"model": "Traditional-STT", "avgWer": 0.204}
                ]
            }
        }

class BlogPostResponse(BlogPostBase):
    """Schema for blog post responses including system-generated fields"""
    id: str = Field(..., description="Unique identifier for the blog post", example="550e8400-e29b-41d4-a716-446655440000")
    date: datetime = Field(..., description="Publication date and time", example="2025-12-04T10:30:00Z")

    class Config:
        from_attributes = True

# Dashboard Data schemas
class DashboardDataRow(BaseModel):
    audio_file_name: str = None
    audio_length: float = None
    model: str = None
    ground_truth: str = None
    transcription: str = None
    wer_score: float = None
    inference_time: float = None
    
    class Config:
        # Allow field names with different cases
        populate_by_name = True
        # Define field aliases for the exact frontend field names
        fields = {
            'audio_file_name': 'Audio File Name',
            'audio_length': 'Audio Length', 
            'model': 'Model',
            'ground_truth': 'Ground_truth',
            'transcription': 'Transcription',
            'wer_score': 'WER Score',
            'inference_time': 'Inference time (in sec)'
        }

class FileUploadResponse(BaseModel):
    """Response schema for file upload processing"""
    data: List[dict] = Field(..., description="Processed benchmark data from uploaded file")
    message: str = Field(default="File processed successfully", description="Processing status message", example="Successfully processed 150 rows from benchmark_results.xlsx")
    
    class Config:
        json_schema_extra = {
            "example": {
                "data": [
                    {
                        "Audio File Name": "sample_001.wav",
                        "Audio Length": 12.5,
                        "Model": "Whisper-large",
                        "Ground_truth": "hello world this is a test",
                        "Transcription": "hello world this is a test",
                        "WER Score": 0.0,
                        "Inference time (in sec)": 2.3
                    }
                ],
                "message": "Successfully processed 150 rows from benchmark_results.xlsx"
            }
        }

# AI Service schemas
class SummarizeRequest(BaseModel):
    """Request schema for text summarization"""
    content: str = Field(..., description="Text content to summarize", min_length=10, example="This is a detailed analysis of ASR model performance showing that Whisper achieves superior accuracy with 12.3% WER compared to traditional models at 18.7% WER, though with increased computational requirements.")

class SummarizeResponse(BaseModel):
    """Response schema for text summarization"""
    summary: str = Field(..., description="AI-generated concise summary", example="Whisper outperforms traditional ASR models with 12.3% vs 18.7% WER, but requires more computational resources.")

class BlogGenerationData(BaseModel):
    """Input data for AI blog post generation"""
    summaryStats: dict = Field(..., description="Overall benchmark statistics", example={"totalFiles": 150, "avgWer": 0.156, "avgInferenceTime": 2.34})
    modelPerformance: List[dict] = Field(..., description="Per-model performance data", example=[{"model": "Whisper", "avgWer": 0.123, "avgInferenceTime": 3.2}])
    fileName: str = Field(..., description="Source file name for context", example="benchmark_results_2025.xlsx")

class BlogPostOutput(BaseModel):
    """AI-generated blog post output"""
    title: str = Field(..., description="Generated blog post title", example="Comprehensive ASR Benchmark Analysis: Whisper vs Traditional Models")
    excerpt: str = Field(..., description="Generated excerpt/summary", example="Latest benchmarking reveals significant accuracy improvements with modern transformer-based ASR models.")
    content: str = Field(..., description="Full HTML blog post content", example="<h2>Executive Summary</h2><p>Our comprehensive analysis...</p>")

class AnalyzeErrorsRequest(BaseModel):
    """Request schema for transcription error analysis"""
    ground_truth: str = Field(..., description="Correct transcription text", example="The quick brown fox jumps over the lazy dog")
    transcription: str = Field(..., description="ASR model output to analyze", example="The quick brown fox jumps over the lady dog")

class TranscriptionError(BaseModel):
    """Individual transcription error details"""
    type: str = Field(..., description="Error type", enum=["Substitution", "Deletion", "Insertion"], example="Substitution")
    ground_truth_segment: str = Field(..., description="Correct text segment", example="lazy")
    transcription_segment: str = Field(..., description="Transcribed text segment", example="lady")

class AnalysisResult(BaseModel):
    """Transcription error analysis results"""
    summary: str = Field(..., description="Overall quality assessment", example="High accuracy transcription with 1 substitution error affecting word recognition.")
    errors: List[TranscriptionError] = Field(..., description="Detailed error breakdown")

class CompareModelsRequest(BaseModel):
    """Request schema for model comparison"""
    model_a: dict = Field(..., description="First model data with name and benchmark results", example={"name": "Whisper", "data": [{"WER Score": 0.12, "Inference time (in sec)": 3.2}]})
    model_b: dict = Field(..., description="Second model data with name and benchmark results", example={"name": "Traditional STT", "data": [{"WER Score": 0.18, "Inference time (in sec)": 1.8}]})

class HeadToHeadAnalysis(BaseModel):
    """Head-to-head model comparison results"""
    winner: str = Field(..., description="Overall winning model", example="Whisper")
    summary: str = Field(..., description="Executive summary of comparison", example="Whisper demonstrates superior accuracy but with increased computational requirements.")
    accuracyAnalysis: str = Field(..., description="Detailed accuracy comparison", example="Whisper achieves 12% WER vs Traditional STT's 18% WER, representing a 33% improvement in accuracy.")
    speedAnalysis: str = Field(..., description="Performance and speed analysis", example="Traditional STT processes audio 1.8x faster but at the cost of accuracy.")

# ===== USER & AUTHENTICATION SCHEMAS =====

class UserBase(BaseModel):
    """Base user schema"""
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    email: EmailStr = Field(..., description="User email address")
    full_name: Optional[str] = Field(None, max_length=100, description="Full display name")
    bio: Optional[str] = Field(None, max_length=500, description="User biography")

class UserCreate(UserBase):
    """Schema for user registration"""
    password: str = Field(..., min_length=8, description="User password (min 8 characters)")
    confirm_password: str = Field(..., description="Password confirmation")

class UserUpdate(BaseModel):
    """Schema for updating user profile"""
    full_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = Field(None, description="Avatar image URL")
    preferences: Optional[Dict[str, Any]] = Field(None, description="User preferences")

class UserAdminUpdate(UserUpdate):
    """Schema for admin user updates"""
    role: Optional[UserRole] = Field(None, description="User role")
    status: Optional[UserStatus] = Field(None, description="User status")

class UserResponse(UserBase):
    """Schema for user responses"""
    id: str
    role: UserRole
    status: UserStatus
    avatar_url: Optional[str] = None
    last_login: Optional[datetime] = None
    created_at: datetime
    is_email_verified: bool
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    """Schema for user login"""
    username_or_email: str = Field(..., description="Username or email address")
    password: str = Field(..., description="User password")

class TokenResponse(BaseModel):
    """Schema for token responses"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse

class RefreshTokenRequest(BaseModel):
    """Schema for token refresh"""
    refresh_token: str

class PasswordResetRequest(BaseModel):
    """Schema for password reset request"""
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation"""
    token: str
    new_password: str = Field(..., min_length=8)
    confirm_password: str

# ===== AUDIT LOG SCHEMAS =====

class AuditLogResponse(BaseModel):
    """Schema for audit log responses"""
    id: str
    user_id: Optional[str]
    action: str
    resource_type: Optional[str]
    resource_id: Optional[str]
    details: Optional[Dict[str, Any]]
    ip_address: Optional[str]
    timestamp: datetime
    
    class Config:
        from_attributes = True

# ===== ADMIN SCHEMAS =====

class SystemStatsResponse(BaseModel):
    """Schema for system statistics"""
    total_users: int
    active_users: int
    total_posts: int
    total_uploads: int
    recent_activities: List[AuditLogResponse]
    user_growth: List[Dict[str, Any]]
    popular_models: List[Dict[str, Any]]
    tradeOffs: str = Field(..., description="Trade-off analysis and recommendations", example="Choose Whisper for batch processing where accuracy is critical; use Traditional STT for real-time applications.")


seed_data.py
from sqlalchemy.orm import Session
from models import BlogPost
from datetime import datetime

def seed_database(db: Session):
    """Seed the database with initial data if it's empty"""
    
    # Check if we already have posts
    existing_posts = db.query(BlogPost).first()
    if existing_posts:
        return  # Database already seeded
    
    # Create some sample blog posts
    sample_posts = [
        {
            "title": "Whisper vs Speech-to-Text: A Comprehensive Benchmark Analysis",
            "author": "ASR Research Team",
            "excerpt": "An in-depth comparison of OpenAI's Whisper model against traditional speech-to-text solutions, analyzing accuracy, speed, and resource consumption across diverse audio datasets.",
            "content": """<h2>Executive Summary</h2>
<p>This comprehensive analysis examines the performance characteristics of OpenAI's Whisper model compared to traditional speech-to-text solutions. Our benchmarking reveals significant insights into accuracy improvements and computational trade-offs.</p>

<h2>Methodology</h2>
<p>We evaluated both models across multiple datasets including:</p>
<ul>
<li>LibriSpeech clean and noisy subsets</li>
<li>Common Voice multilingual samples</li>
<li>Custom domain-specific recordings</li>
</ul>

<h2>Key Findings</h2>
<p>Whisper demonstrated superior accuracy with an average WER of 12.3% compared to 18.7% for traditional models. However, inference time increased by approximately 40% due to the transformer architecture's computational requirements.</p>

<h2>Recommendations</h2>
<p>For real-time applications, traditional models remain viable. For batch processing where accuracy is paramount, Whisper provides significant value despite the computational overhead.</p>""",
            "benchmark_data": [
                {"model": "Whisper", "wer": 12.3, "dataset": "LibriSpeech"},
                {"model": "Traditional STT", "wer": 18.7, "dataset": "LibriSpeech"},
                {"model": "Whisper", "wer": 15.2, "dataset": "Common Voice"},
                {"model": "Traditional STT", "wer": 22.1, "dataset": "Common Voice"}
            ],
            "model_performance_data": [
                {"model": "Whisper", "avgWer": 13.75},
                {"model": "Traditional STT", "avgWer": 20.4}
            ]
        },
        {
            "title": "Multilingual ASR Performance: Breaking Language Barriers",
            "author": "Global AI Research",
            "excerpt": "Exploring how modern automatic speech recognition systems perform across different languages and accents, with special focus on low-resource languages.",
            "content": """<h2>Introduction</h2>
<p>As ASR technology advances, understanding its performance across diverse linguistic landscapes becomes crucial for global applications.</p>

<h2>Cross-Language Analysis</h2>
<p>Our study encompassed 15 languages, ranging from high-resource languages like English and Mandarin to low-resource languages such as Welsh and Amharic.</p>

<h2>Results</h2>
<p>High-resource languages achieved average WERs below 10%, while low-resource languages showed WERs ranging from 25-40%. Interestingly, multilingual models showed more consistent performance across all languages compared to language-specific models.</p>""",
            "benchmark_data": [
                {"model": "Multilingual Model", "wer": 9.2, "dataset": "English"},
                {"model": "Multilingual Model", "wer": 11.8, "dataset": "Mandarin"},
                {"model": "Multilingual Model", "wer": 28.4, "dataset": "Welsh"},
                {"model": "Language-specific", "wer": 7.1, "dataset": "English"}
            ],
            "model_performance_data": [
                {"model": "Multilingual Model", "avgWer": 16.5},
                {"model": "Language-specific", "avgWer": 12.8}
            ]
        }
    ]
    
    for post_data in sample_posts:
        db_post = BlogPost(
            title=post_data["title"],
            author=post_data["author"], 
            excerpt=post_data["excerpt"],
            content=post_data["content"],
            benchmark_data=post_data.get("benchmark_data"),
            model_performance_data=post_data.get("model_performance_data"),
            date=datetime.utcnow()
        )
        db.add(db_post)
    
    db.commit()
    print("Database seeded with sample data")
