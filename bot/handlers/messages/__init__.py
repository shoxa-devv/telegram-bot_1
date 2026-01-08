from aiogram import Router

from .admin_input import router as admin_input_router
from .forwarded import router as forwarded_router
from .photo import router as photo_router
from .state_flows import router as state_flows_router
from .text import router as text_router
from .voice import router as voice_router

router = Router()
router.include_router(state_flows_router)
router.include_router(admin_input_router)
router.include_router(forwarded_router)
router.include_router(photo_router)
router.include_router(voice_router)
router.include_router(text_router)

