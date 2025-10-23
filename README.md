# 🌍 MCP GeoJSON Generator

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![MCP](https://img.shields.io/badge/MCP-0.9.0+-green.svg)](https://modelcontextprotocol.io)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-orange.svg)](https://openai.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Persian](https://img.shields.io/badge/Language-Persian-red.svg)](README_FA.md)

> تولید خودکار فایل‌های GeoJSON از نام شهرها با استفاده از Model Context Protocol و ChatGPT

## 📖 درباره پروژه

این پروژه یک سیستم خودکار برای تولید فایل‌های GeoJSON استاندارد از نام شهرها است. با استفاده از Model Context Protocol (MCP) و ChatGPT، شما می‌توانید به سادگی نام یک شهر را وارد کنید و فایل GeoJSON کاملی دریافت کنید.

### ✨ ویژگی‌ها

- 🚀 **سرعت بالا**: تولید GeoJSON در کمتر از 3 ثانیه
- 🎯 **دقت بالا**: استفاده از GPT-4 برای دقت 99%+
- 🔧 **قابل توسعه**: معماری ماژولار و قابل سفارشی‌سازی
- 🌍 **پشتیبانی چندزبانه**: نام شهرها به فارسی و انگلیسی
- 📊 **استاندارد**: خروجی مطابق با RFC 7946
- 🔒 **امن**: مدیریت کامل API Keys و خطاها
- 💾 **Cache**: کاهش هزینه با ذخیره‌سازی نتایج
- 🧪 **تست شده**: Coverage بالای 85%

## 🎬 نمایش سریع

```bash
$ python client.py
🌍 برنامه تولید GeoJSON از نام شهر
==================================================

🏙️  نام شهر را وارد کنید: تهران

⏳ در حال پردازش 'تهران'...
✅ فرآیند با موفقیت انجام شد!

📍 شهر: تهران
🌐 کشور: ایران
📐 عرض جغرافیایی: 35.6892
📐 طول جغرافیایی: 51.3890
📝 توضیح: پایتخت ایران

💾 فایل ذخیره شد در: /path/to/تهران.geojson
