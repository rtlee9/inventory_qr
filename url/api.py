import json
import logging
import os
import re
from functools import wraps

from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from utils.qr import gen_qr
from utils.url import create, delete, track, update

from .models import UrlAction

logger = logging.getLogger(__name__)

URL_KEY_RE = re.compile(r"^[a-zA-Z0-9-]+$")


def require_api_key(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        api_key = os.getenv("API_KEY")
        if not api_key:
            return JsonResponse({"error": "API_KEY not configured on server"}, status=500)
        provided = request.headers.get("X-API-Key", "")
        if provided != api_key:
            return JsonResponse({"error": "Invalid or missing API key"}, status=401)
        return view_func(request, *args, **kwargs)

    return wrapper


def _get_api_user():
    user_id = os.getenv("API_USER_ID")
    if user_id:
        return User.objects.get(pk=int(user_id))
    return User.objects.filter(is_superuser=True).first()


def _save_action(result, user):
    """Save a UrlAction from a utils.url result dict."""
    action = UrlAction.objects.create(
        action_type=result["action_type"],
        long_url=result.get("long_url"),
        response_json=result["response_json"],
        response_code=result["response_code"],
        url_key=result["url_key"],
        user=user,
    )
    return action


@csrf_exempt
@require_api_key
@require_http_methods(["GET", "POST"])
def url_list(request):
    """GET: list recent actions. POST: create a shortened URL."""
    if request.method == "GET":
        actions = UrlAction.objects.order_by("-pk")[:50]
        data = [
            {
                "id": a.id,
                "action_type": a.action_type,
                "url_key": a.url_key,
                "long_url": a.long_url,
                "response_code": a.response_code,
                "success": a.was_successfull(),
                "timestamp": a.timestamp.isoformat(),
            }
            for a in actions
        ]
        return JsonResponse({"results": data})

    # POST — create
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    long_url = body.get("long_url", "").strip()
    key = body.get("key", "").strip()

    if not long_url:
        return JsonResponse({"error": "long_url is required"}, status=400)
    if not key:
        return JsonResponse({"error": "key is required"}, status=400)
    if not URL_KEY_RE.match(key):
        return JsonResponse(
            {"error": "key can only contain letters, numbers, and hyphens"},
            status=400,
        )

    user = _get_api_user()
    if not user:
        return JsonResponse({"error": "No API user available"}, status=500)

    result = create(long_url, key)
    action = _save_action(result, user)

    return JsonResponse(
        {
            "id": action.id,
            "action_type": action.action_type,
            "url_key": action.url_key,
            "long_url": action.long_url,
            "response_code": action.response_code,
            "success": action.was_successfull(),
            "short_url": f"https://aws3.link/{key}",
        },
        status=201,
    )


@csrf_exempt
@require_api_key
@require_http_methods(["GET", "PUT", "DELETE"])
def url_detail(request, key):
    """GET: detail + history. PUT: update target. DELETE: delete."""
    if not URL_KEY_RE.match(key):
        return JsonResponse(
            {"error": "Invalid key format"}, status=400
        )

    if request.method == "GET":
        actions = UrlAction.objects.filter(url_key=key).order_by("-pk")
        if not actions.exists():
            return JsonResponse({"error": "No actions found for this key"}, status=404)
        data = [
            {
                "id": a.id,
                "action_type": a.action_type,
                "url_key": a.url_key,
                "long_url": a.long_url,
                "response_code": a.response_code,
                "success": a.was_successfull(),
                "timestamp": a.timestamp.isoformat(),
            }
            for a in actions
        ]
        return JsonResponse({"url_key": key, "history": data})

    user = _get_api_user()
    if not user:
        return JsonResponse({"error": "No API user available"}, status=500)

    if request.method == "PUT":
        try:
            body = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({"error": "Invalid JSON body"}, status=400)

        long_url = body.get("long_url", "").strip()
        if not long_url:
            return JsonResponse({"error": "long_url is required"}, status=400)

        results = update(key, long_url)
        # update() returns [delete_result, create_result]
        response_code = max(r["response_code"] for r in results)
        action = UrlAction.objects.create(
            action_type="update",
            long_url=long_url,
            response_json=[r["response_json"] for r in results],
            response_code=response_code,
            url_key=key,
            user=user,
        )
        return JsonResponse(
            {
                "id": action.id,
                "action_type": "update",
                "url_key": key,
                "long_url": long_url,
                "response_code": response_code,
                "success": action.was_successfull(),
                "short_url": f"https://aws3.link/{key}",
            }
        )

    # DELETE
    result = delete(key)
    action = _save_action(result, user)
    return JsonResponse(
        {
            "id": action.id,
            "action_type": "delete",
            "url_key": key,
            "response_code": action.response_code,
            "success": action.was_successfull(),
        }
    )


@require_api_key
@require_http_methods(["GET"])
def url_track(request, key):
    """Get tracking/hit data for a key."""
    if not URL_KEY_RE.match(key):
        return JsonResponse({"error": "Invalid key format"}, status=400)

    data = track(key)
    return JsonResponse({"url_key": key, "tracking": data})


@require_api_key
@require_http_methods(["GET"])
def url_qr(request, key):
    """Get QR code URL for a key."""
    if not URL_KEY_RE.match(key):
        return JsonResponse({"error": "Invalid key format"}, status=400)

    short_url = f"https://aws3.link/{key}"
    qr_url = gen_qr(short_url)
    return JsonResponse({"url_key": key, "short_url": short_url, "qr_url": qr_url})
