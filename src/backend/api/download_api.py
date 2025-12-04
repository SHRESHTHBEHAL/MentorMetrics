from fastapi import APIRouter, HTTPException, Request, Response
from src.backend.services.session_service import SessionService
from src.backend.services.user_service import UserService
from src.backend.utils.logger import setup_logger
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO

logger = setup_logger(__name__)

router = APIRouter()

@router.get("/report/{session_id}")
def download_report_endpoint(session_id: str, request: Request):
    
    logger.info(f"[API] GET /download/report/{session_id} - PDF report requested")
    
    user_id = UserService.get_user_id(request)
    
    try:
        session = SessionService.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
            
        if session.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized")
            
        from src.backend.api.results_api import get_session_results
        results = get_session_results(session_id, request)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[API] Error fetching session data: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch session data")

    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#4F46E5') # Indigo-600
        )
        story.append(Paragraph("Evaluation Report", title_style))
        story.append(Paragraph(f"Session ID: {session_id}", styles['Normal']))
        story.append(Spacer(1, 20))

        story.append(Paragraph("Scores", styles['Heading2']))
        
        scores_data = [
            ["Metric", "Score"],
            ["Mentor Score", f"{results.get('scores', {}).get('mentor_score', 0):.1f}/10"],
            ["Communication Clarity", f"{results.get('scores', {}).get('communication_clarity', 0):.1f}/10"],
            ["Engagement", f"{results.get('scores', {}).get('engagement', 0):.1f}/10"],
            ["Technical Correctness", f"{results.get('scores', {}).get('technical_correctness', 0):.1f}/10"],
            ["Pacing & Structure", f"{results.get('scores', {}).get('pacing_structure', 0):.1f}/10"],
            ["Interactive Quality", f"{results.get('scores', {}).get('interactive_quality', 0):.1f}/10"]
        ]
        
        t = Table(scores_data, colWidths=[200, 100])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#EEF2FF')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#3730A3')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E5E7EB'))
        ]))
        story.append(t)
        story.append(Spacer(1, 20))

        report_data = results.get('report') or {}
        story.append(Paragraph("Executive Summary", styles['Heading2']))
        story.append(Paragraph(report_data.get('summary', 'No summary available.'), styles['Normal']))
        story.append(Spacer(1, 20))

        story.append(Paragraph("Strengths", styles['Heading2']))
        for strength in report_data.get('strengths', []):
            story.append(Paragraph(f"• {strength}", styles['Normal']))
        story.append(Spacer(1, 20))

        story.append(Spacer(1, 20))

        story.append(Paragraph("Performance Metrics", styles['Heading2']))
        
        audio = results.get('audio', {})
        visual = results.get('visual', {})
        
        metrics_data = [
            ["Category", "Metric", "Value"],
            ["Audio", "WPM", f"{audio.get('wpm', 'N/A')}"],
            ["", "Silence Ratio", f"{(audio.get('silence_ratio', 0) * 100):.1f}%" if audio.get('silence_ratio') else "N/A"],
            ["", "Clarity Score", f"{audio.get('clarity_score', 'N/A')}/10"],
            ["Visual", "Face Visibility", f"{visual.get('face_visibility_score', 'N/A')}/10"],
            ["", "Gaze Forward", f"{visual.get('gaze_forward_score', 'N/A')}/10"],
            ["", "Gesture Score", f"{visual.get('gesture_score', 'N/A')}/10"],
            ["", "Movement Score", f"{visual.get('movement_score', 'N/A')}/10"]
        ]
        
        t2 = Table(metrics_data, colWidths=[80, 140, 80])
        t2.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#EEF2FF')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#3730A3')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E5E7EB'))
        ]))
        story.append(t2)
        story.append(Spacer(1, 20))

        story.append(Paragraph("Areas for Improvement", styles['Heading2']))
        for improvement in report_data.get('improvements', []):
            story.append(Paragraph(f"• {improvement}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        story.append(Paragraph("Actionable Tips", styles['Heading2']))
        for tip in report_data.get('actionable_tips', []):
            story.append(Paragraph(f"• {tip}", styles['Normal']))
        story.append(Spacer(1, 20))

        doc.build(story)
        buffer.seek(0)
        
        return Response(
            content=buffer.getvalue(),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=report-{session_id}.pdf"}
        )

    except Exception as e:
        logger.error(f"[API] Error generating PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF: {str(e)}")

@router.get("/raw/{session_id}")
def download_raw_data_endpoint(session_id: str, request: Request):
    
    logger.info(f"[API] GET /download/raw/{session_id} - Raw data requested")
    
    user_id = UserService.get_user_id(request)
    
    try:
        session = SessionService.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
            
        if session.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized")
            
        from src.backend.api.results_api import get_session_results
        results = get_session_results(session_id, request)
        
        import json
        json_str = json.dumps(results, indent=2, default=str)
        
        return Response(
            content=json_str,
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=mentor-metrics-session-{session_id}.json"}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[API] Error fetching raw data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch raw data: {str(e)}")
