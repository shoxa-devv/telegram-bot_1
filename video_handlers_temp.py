# Video generation handlers to add to main.py

# 1. Quality selection keyboard function (add after other keyboard functions)
def video_quality_keyboard(user_id: int) -> InlineKeyboardMarkup:
    """Video sifatini tanlash klaviaturasi"""
    kb = InlineKeyboardBuilder()
    kb.button(text=get_text(user_id, "quality_480p"), callback_data="video_quality_480p")
    kb.button(text=get_text(user_id, "quality_720p"), callback_data="video_quality_720p")
    kb.button(text=get_text(user_id, "quality_1080p"), callback_data="video_quality_1080p")
    kb.button(text=get_text(user_id, "quality_4k"), callback_data="video_quality_4k")
    kb.button(text=get_text(user_id, "back"), callback_data="back_to_main")
    kb.adjust(1)
    return kb.as_markup()


# 2. Video quality callback handler (add to menu_callback or create new callback handler)
@dp.callback_query(F.data.startswith("video_quality_"))
async def video_quality_callback(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    quality = callback.data.split("_")[-1]  # Extract quality (480p, 720p, etc.)
    
    if user_id not in USER_STATES or USER_STATES[user_id].get("state") != "waiting_video_quality":
        await callback.answer("Xatolik: Avval video tavsifini yuboring", show_alert=True)
        return
    
    # Get video description from state
    video_description = USER_STATES[user_id].get("video_description", "")
    
    # Clear state
    del USER_STATES[user_id]
    
    # Check limit
    if not user_manager.check_limit(user_id):
        kb = InlineKeyboardBuilder()
        kb.button(text=get_text(user_id, "buy_premium"), callback_data="menu_premium")
        await callback.message.edit_text(get_text(user_id, "limit_reached"), reply_markup=kb.as_markup())
        return
    
    user_manager.increment_usage(user_id)
    
    # Show generating message
    await callback.message.edit_text(get_text(user_id, "video_generating"))
    
    try:
        # Import video generator
        from video_generator import generate_video, download_video
        import os
        
        # Generate video
        video_url = generate_video(video_description, quality)
        
        # Download video
        os.makedirs("videos", exist_ok=True)
        video_path = f"videos/{user_id}_{quality}.mp4"
        download_video(video_url, video_path)
        
        # Send video
        await callback.message.answer(get_text(user_id, "video_success"))
        with open(video_path, 'rb') as video_file:
            await bot.send_video(
                callback.message.chat.id,
                video_file,
                caption=f"🎬 {video_description[:100]}..."
            )
        
        # Clean up
        os.remove(video_path)
        
        # Show main menu
        await callback.message.answer(
            get_text(user_id, "main_menu"),
            reply_markup=main_menu_keyboard(user_id)
        )
        
    except Exception as e:
        await callback.message.answer(
            f"{get_text(user_id, 'video_error')}\\n\\nError: {str(e)}"
        )
        await callback.message.answer(
            get_text(user_id, "main_menu"),
            reply_markup=main_menu_keyboard(user_id)
        )
    
    await callback.answer()


# 3. Video description input handler (add after admin_input_handler)
@dp.message(lambda msg: msg.from_user.id in USER_STATES and USER_STATES[msg.from_user.id].get("state") == "waiting_video_description")
async def video_description_handler(msg: types.Message):
    user_id = msg.from_user.id
    video_description = msg.text.strip()
    
    if not video_description or len(video_description) < 10:
        await msg.answer("Iltimos, video tavsifini batafsil yozing (kamida 10 ta belgi)")
        return
    
    # Save description and move to quality selection
    USER_STATES[user_id] = {
        "state": "waiting_video_quality",
        "video_description": video_description
    }
    
    await msg.answer(
        get_text(user_id, "video_quality_select"),
        reply_markup=video_quality_keyboard(user_id)
    )
