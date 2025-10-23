from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp import types
from openai import OpenAI
import json
import os
from dotenv import load_dotenv
from datetime import datetime

# بارگذاری تنظیمات
load_dotenv()

# تنظیمات OpenAI
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
)
MODEL = os.getenv("OPENAI_MODEL", "gpt-4")

# ایجاد سرور
server = Server("geojson-mcp-server")


def get_city_coordinates(city_name: str) -> dict:
    """دریافت مختصات شهر از ChatGPT"""
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "تو یک دستیار جغرافیایی هستی. هنگام درخواست مختصات شهر، تنها JSON را برگردان بدون توضیح اضافی."
                },
                {
                    "role": "user",
                    "content": f"""
                    برای شهر "{city_name}" اطلاعات زیر را به صورت JSON برگردان:
                    {{
                        "city_name": "نام شهر",
                        "latitude": عدد,
                        "longitude": عدد,
                        "country": "کشور",
                        "description": "توضیح کوتاه"
                    }}
                    """
                }
            ],
            temperature=0.5,
            max_tokens=300
        )
        
        content = response.choices[0].message.content.strip()
        
        # تمیز کردن JSON
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
        
        city_data = json.loads(content)
        
        return {
            "success": True,
            "city_data": city_data,
            "model_used": MODEL
        }
        
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": f"خطا در تجزیه JSON: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"خطای عمومی: {str(e)}"
        }


def create_geojson_point(
    city_name: str,
    latitude: float,
    longitude: float,
    properties: dict = None
) -> dict:
    """تولید نقطه GeoJSON"""
    
    if properties is None:
        properties = {}
    
    geojson = {
        "type": "Feature",
        "properties": {
            "name": city_name,
            "timestamp": datetime.now().isoformat(),
            **properties
        },
        "geometry": {
            "type": "Point",
            "coordinates": [longitude, latitude]
        }
    }
    
    return {
        "success": True,
        "geojson": geojson
    }


def save_geojson_file(
    geojson_data: dict,
    file_path: str = "city_point.geojson"
) -> dict:
    """ذخیره GeoJSON در فایل"""
    
    try:
        feature_collection = {
            "type": "FeatureCollection",
            "features": [geojson_data]
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(feature_collection, f, ensure_ascii=False, indent=2)
        
        return {
            "success": True,
            "message": f"فایل با موفقیت ذخیره شد: {file_path}",
            "file_path": os.path.abspath(file_path)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"خطا در ذخیره‌سازی: {str(e)}"
        }


def process_city_to_geojson(city_name: str) -> dict:
    """فرآیند کامل: شهر → مختصات → GeoJSON → فایل"""
    
    print(f"\n🔍 در حال جستجو برای شهر: {city_name}")
    
    # مرحله 1: دریافت مختصات
    coords_result = get_city_coordinates(city_name)
    
    if not coords_result["success"]:
        return coords_result
    
    city_data = coords_result["city_data"]
    print(f"✅ مختصات یافت شد: {city_data}")
    
    # مرحله 2: ایجاد GeoJSON
    geojson_result = create_geojson_point(
        city_name=city_data.get("city_name", city_name),
        latitude=city_data.get("latitude"),
        longitude=city_data.get("longitude"),
        properties={
            "country": city_data.get("country"),
            "description": city_data.get("description")
        }
    )
    
    geojson_data = geojson_result["geojson"]
    print(f"✅ GeoJSON تولید شد")
    
    # مرحله 3: ذخیره در فایل
    file_name = f"{city_name.replace(' ', '_')}.geojson"
    save_result = save_geojson_file(geojson_data, file_name)
    
    if save_result["success"]:
        print(f"✅ {save_result['message']}")
    
    return {
        "success": True,
        "city_data": city_data,
        "geojson": geojson_data,
        "file_info": save_result
    }


# تعریف ابزارها
@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """لیست ابزارهای موجود"""
    return [
        types.Tool(
            name="get_city_coordinates",
            description="دریافت مختصات جغرافیایی یک شهر از ChatGPT",
            inputSchema={
                "type": "object",
                "properties": {
                    "city_name": {
                        "type": "string",
                        "description": "نام شهر به فارسی یا انگلیسی"
                    }
                },
                "required": ["city_name"]
            }
        ),
        types.Tool(
            name="create_geojson_point",
            description="تولید یک نقطه GeoJSON از مختصات",
            inputSchema={
                "type": "object",
                "properties": {
                    "city_name": {"type": "string"},
                    "latitude": {"type": "number"},
                    "longitude": {"type": "number"},
                    "properties": {"type": "object"}
                },
                "required": ["city_name", "latitude", "longitude"]
            }
        ),
        types.Tool(
            name="save_geojson_file",
            description="ذخیره GeoJSON در فایل",
            inputSchema={
                "type": "object",
                "properties": {
                    "geojson_data": {"type": "object"},
                    "file_path": {"type": "string"}
                },
                "required": ["geojson_data"]
            }
        ),
        types.Tool(
            name="process_city_to_geojson",
            description="فرآیند کامل: از نام شهر تا فایل GeoJSON",
            inputSchema={
                "type": "object",
                "properties": {
                    "city_name": {
                        "type": "string",
                        "description": "نام شهر"
                    }
                },
                "required": ["city_name"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(
    name: str,
    arguments: dict
) -> list[types.TextContent]:
    """اجرای ابزارها"""
    
    if name == "get_city_coordinates":
        result = get_city_coordinates(arguments["city_name"])
    elif name == "create_geojson_point":
        result = create_geojson_point(**arguments)
    elif name == "save_geojson_file":
        result = save_geojson_file(**arguments)
    elif name == "process_city_to_geojson":
        result = process_city_to_geojson(arguments["city_name"])
    else:
        result = {"success": False, "error": f"ابزار '{name}' یافت نشد"}
    
    return [
        types.TextContent(
            type="text",
            text=json.dumps(result, ensure_ascii=False, indent=2)
        )
    ]


async def main():
    """اجرای سرور"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="geojson-mcp-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                )
            )
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())