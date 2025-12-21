from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from src.backend.services.analytics_service import AnalyticsService
from src.backend.services.user_service import UserService
from src.backend.utils.supabase_client import supabase
from src.backend.utils.logger import setup_logger
from datetime import datetime, timedelta

logger = setup_logger(__name__)

router = APIRouter()

class FrontendEvent(BaseModel):
    event_name: str
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = {}

@router.post("/analytics/frontend")
def record_frontend_event(
    event: FrontendEvent,
    request: Request,
    background_tasks: BackgroundTasks
):
    
    user_id = None
    try:
        user_id = UserService.get_user_id(request)
    except:
        pass
        
    background_tasks.add_task(
        AnalyticsService.record_event,
        event_name=event.event_name,
        session_id=event.session_id,
        user_id=user_id,
        metadata=event.metadata
    )
    
    return {"status": "recorded"}

@router.get("/analytics/dashboard")
def get_dashboard_analytics(request: Request):
    
    user_id = UserService.get_user_id(request)
    
    logger.info(f"[API] GET /analytics/dashboard - Getting dashboard for user {user_id}")
    
    try:
        response = supabase.table("sessions")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("created_at", desc=True)\
            .execute()
        
        sessions = response.data or []
        
        total_sessions = len(sessions)
        completed_sessions = [s for s in sessions if s.get("status") == "complete"]
        processing_sessions = [s for s in sessions if s.get("status") == "processing"]
        failed_sessions = [s for s in sessions if s.get("status") == "failed"]
        
        metrics = {
            "mentor_score": [],
            "engagement": [],
            "communication_clarity": [],
            "technical_correctness": [],
            "pacing_structure": []
        }
        
        # Get all final_scores for completed sessions
        session_ids = [s["id"] for s in completed_sessions]
        final_scores_map = {}
        if session_ids:
            try:
                fs_response = supabase.table("final_scores")\
                    .select("*")\
                    .in_("session_id", session_ids)\
                    .execute()
                for fs in (fs_response.data or []):
                    final_scores_map[fs["session_id"]] = fs
            except Exception as e:
                logger.warning(f"Failed to fetch final_scores: {e}")
        
        for session in completed_sessions:
            meta = session.get("completion_metadata") or {}
            sid = session["id"]
            fs = final_scores_map.get(sid, {})
            
            # Get mentor_score from metadata or final_scores
            mentor = meta.get("mentor_score") or fs.get("mentor_score")
            if mentor:
                metrics["mentor_score"].append(float(mentor))
            
            # Get other scores from metadata first, then final_scores
            for key in ["engagement", "communication_clarity", "technical_correctness", "pacing_structure"]:
                val = meta.get(key) or fs.get(key)
                if val:
                    metrics[key].append(float(val))
                    
        avgs = {
            k: round(sum(v) / len(v), 2) if v else 0 
            for k, v in metrics.items()
        }
        
        improvement = 0
        scores = metrics["mentor_score"]
        if len(scores) >= 2:
            latest, oldest = scores[0], scores[-1]
            if oldest > 0:
                improvement = round(((latest - oldest) / oldest) * 100, 1)
        
        recent_sessions = [
            {
                "id": s["id"],
                "filename": s["filename"],
                "status": s["status"],
                "created_at": s["created_at"],
                "mentor_score": (s.get("completion_metadata") or {}).get("mentor_score") or final_scores_map.get(s["id"], {}).get("mentor_score")
            }
            for s in sessions[:5]
        ]
        
        score_distribution = {
            "0-2": 0, "2-4": 0, "4-6": 0, "6-8": 0, "8-10": 0
        }
        for score in scores:
            if score < 2: score_distribution["0-2"] += 1
            elif score < 4: score_distribution["2-4"] += 1
            elif score < 6: score_distribution["4-6"] += 1
            elif score < 8: score_distribution["6-8"] += 1
            else: score_distribution["8-10"] += 1
        
        score_history = []
        for s in completed_sessions[:10][::-1]:
            meta = s.get("completion_metadata") or {}
            fs = final_scores_map.get(s["id"], {})
            score = meta.get("mentor_score") or fs.get("mentor_score")
            if score:
                score_history.append({
                    "date": s["created_at"][:10],
                    "score": float(score)
                })

        
        return {
            "summary": {
                "total_sessions": total_sessions,
                "completed_sessions": len(completed_sessions),
                "processing_sessions": len(processing_sessions),
                "failed_sessions": len(failed_sessions),
                "avg_mentor_score": avgs["mentor_score"],
                "avg_engagement": avgs["engagement"],
                "avg_communication": avgs["communication_clarity"],
                "avg_technical": avgs["technical_correctness"],
                "avg_pacing": avgs["pacing_structure"],
                "improvement_percent": improvement
            },
            "recent_sessions": recent_sessions,
            "score_distribution": score_distribution,
            "score_history": score_history
        }
        
    except Exception as e:
        logger.error(f"[API] Error getting dashboard analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard analytics: {str(e)}")
