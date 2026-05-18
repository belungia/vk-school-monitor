import lmstudio as lms

from src.agent.schemas import AnalyzedSchema
from src.db.methods.post import get_unanalyzed_posts, update_statuses
from src.db.methods.alert import add_alerts


system_prompt = (
    "You are a psychologist who analyzes input text and identifies destructive content. "
    "Destructive content includes signs of violence, name-calling, suicide, and other related things. "
    "Lies are not considered destructive content. "
    "The input text will most often be in Russian, but may also be in other languages; "
    "your response should not change based on the language. "
    "Your task is to respond in JSON format with the following keys: "
    '"destructive" - key for destructive content, True/False, '
    '"reason" - a quote from the text on which you based your decision about destructive content. '
    "If destructive is False, reason must be an empty string (\"\"). "
    "No additional text, only JSON."
)


async def analyze_posts():
    destructive_posts = []
    processed_ids = []
    posts = await get_unanalyzed_posts()
    async with lms.AsyncClient(api_host="localhost:1234") as client:
        model = await client.llm.model("qwen/qwen3.5-9b")
        
        for post in posts:
            try:
                if len(post) < 3:
                    raise ValueError(f"Post кортеж имеет длину {len(post)}, ожидается 3")
                post_id, user_id, text = post[0], post[1], post[2]
                
                if len(text) > 12000:
                    text = text[:12000] + "..."
                
                chat = lms.Chat(system_prompt)
                chat.add_user_message(f"Text:\n{text}")
                
                result = await model.respond(
                    chat,
                    response_format=AnalyzedSchema,
                    config={"temperature": 0.0, "timeout": 60.0}
                )
                analyze = result.parsed
                print(analyze)

                if analyze.get("destructive"):
                    destructive_posts.append({
                        "post_id": post_id,
                        "user_id": user_id,
                        "reason": analyze.get("reason", "")
                    })
                
                processed_ids.append(post_id)
                
            except Exception as e:
                print(f"Ошибка при анализе поста {post[0] if post else '?'}: {e}")
                continue

        await add_alerts(destructive_posts)
        await update_statuses(processed_ids)
    
    return True