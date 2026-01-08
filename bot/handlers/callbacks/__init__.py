from aiogram import Router

from .admin import router as admin_router
from .image import router as image_router
from .language import router as language_router
from .menu import router as menu_router
from .payments import router as payments_router
from .subscription import router as subscription_router
from .video import router as video_router

router = Router()
router.include_router(subscription_router)
router.include_router(language_router)
router.include_router(menu_router)
router.include_router(admin_router)
router.include_router(video_router)
router.include_router(image_router)
router.include_router(payments_router)

