from fastapi import APIRouter, HTTPException, Query

from controllers.NlpController import NlpController
from routes.schema.nlp import PushDataRequest, SearchRequest

router = APIRouter(prefix="/api/nlp", tags=["nlp"])

nlp_controller = NlpController()


@router.get("/info")
def info():
  return nlp_controller.info()


@router.post("/index/push")
def index_push(request: PushDataRequest):
  return nlp_controller.index_push(request.do_reset)


@router.post("/search")
def search(request: SearchRequest):
  try:
    matches = nlp_controller.search(request.text, request.top_k)
  except ValueError as exc:
    raise HTTPException(status_code=400, detail=str(exc))
  return {"matches": matches}


@router.post("/answer")
def answer(request: SearchRequest, locale: str = Query("en", min_length=2, max_length=5)):
  try:
    return nlp_controller.answer(request.text, request.top_k, locale)
  except ValueError as exc:
    raise HTTPException(status_code=400, detail=str(exc))
