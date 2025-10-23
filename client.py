import asyncio
import json
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["server.py"],
    )
    
    async with AsyncExitStack() as stack:
        # اتصال به سرور
        stdio_transport = await stack.enter_async_context(stdio_client(server_params))
        stdio, write = stdio_transport
        session = await stack.enter_async_context(ClientSession(stdio, write))
        
        # Initialize
        await session.initialize()
        
        # دریافت نام شهر
        print("=" * 50)
        print("🌍 برنامه تولید GeoJSON از نام شهر")
        print("=" * 50)
        
        city_name = input("\n🏙️  نام شهر را وارد کنید: ").strip()
        
        if not city_name:
            print("❌ نام شهر نمی‌تواند خالی باشد!")
            return
        
        print(f"\n⏳ در حال پردازش '{city_name}'...")
        
        # فراخوانی ابزار
        result = await session.call_tool(
            "process_city_to_geojson",
            arguments={"city_name": city_name}
        )
        
        # پردازش نتیجه
        response_text = result.content[0].text
        data = json.loads(response_text)
        
        if data["success"]:
            print("\n✅ فرآیند با موفقیت انجام شد!\n")
            
            city_data = data["city_data"]
            print(f"📍 شهر: {city_data.get('city_name')}")
            print(f"🌐 کشور: {city_data.get('country')}")
            print(f"📐 عرض جغرافیایی: {city_data.get('latitude')}")
            print(f"📐 طول جغرافیایی: {city_data.get('longitude')}")
            print(f"📝 توضیح: {city_data.get('description')}")
            
            print("\n📄 GeoJSON تولید شده:")
            print(json.dumps(data["geojson"], ensure_ascii=False, indent=2))
            
            file_path = data["file_info"].get("file_path")
            print(f"\n💾 فایل ذخیره شد در: {file_path}")
        else:
            print(f"\n❌ خطا: {data.get('error')}")


if __name__ == "__main__":
    asyncio.run(main())