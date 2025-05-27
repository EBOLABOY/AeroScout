import sqlalchemy
from sqlalchemy import (
    Table, Column, Integer, String, Boolean, DateTime, Text, Float, ForeignKey, func
)
from app.database.connection import metadata

# User table definition
users_table = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String(100), nullable=False),
    Column("email", String(255), unique=True, index=True, nullable=False),
    Column("hashed_password", String(255), nullable=False),
    Column("is_admin", Boolean, default=False, nullable=False),
    Column("is_active", Boolean, default=True, nullable=False),
    Column("created_at", DateTime, default=func.now(), nullable=False),
    Column("last_login_at", DateTime, nullable=True),
    Column("api_call_count_today", Integer, default=0, nullable=False),
    Column("last_api_call_date", DateTime, nullable=True), # Consider Date type if only date matters
)

# Invitation code table definition
invitation_codes_table = Table(
    "invitation_codes",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("code", String(64), unique=True, index=True, nullable=False),
    Column("is_used", Boolean, default=False, nullable=False),
    # Nullable allows codes created by system/admin not tied to a specific user
    Column("created_by_user_id", Integer, ForeignKey("users.id"), nullable=True),
    Column("used_by_user_id", Integer, ForeignKey("users.id"), nullable=True),
    Column("created_at", DateTime, default=func.now(), nullable=False),
    Column("used_at", DateTime, nullable=True),
)

# Generic location cache table (from various sources like Kiwi/Trip.com)
locations_table = Table(
    "locations",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("query", String(255), index=True, nullable=False), # The search term used
    Column("trip_type", String(50), nullable=True), # e.g., 'oneway', 'round'
    Column("mode", String(50), nullable=True), # e.g., 'airport', 'city', 'station'
    # Removed name, code, country, city, type, data_source as per requirement
    Column("raw_data", Text, nullable=True), # Store the original JSON/data
    Column("created_at", DateTime, default=func.now(), nullable=False),
    Column("updated_at", DateTime, default=func.now(), onupdate=func.now(), nullable=False),
)

# More structured airport cache table
airports_table = Table(
    "airports",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(255), nullable=False),
    Column("iata_code", String(3), unique=True, index=True, nullable=False),
    Column("icao_code", String(4), unique=True, index=True, nullable=True),
    Column("city", String(100), nullable=True),
    Column("country", String(100), nullable=True),
    Column("latitude", Float, nullable=True),
    Column("longitude", Float, nullable=True),
    Column("data_source", String(50), nullable=True), # e.g., 'openflights', 'manual'
    Column("raw_data", Text, nullable=True), # Store additional data if needed
    Column("created_at", DateTime, default=func.now(), nullable=False),
    Column("updated_at", DateTime, default=func.now(), onupdate=func.now(), nullable=False),
)

# Table for potential hub airports used in probing tasks
potential_hubs_table = Table(
    "potential_hubs",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(255), nullable=True), # Name might not always be available initially
    Column("iata_code", String(3), unique=True, index=True, nullable=False),
    Column("city", String(100), nullable=True),
    Column("country", String(100), nullable=True),
    Column("country_code", String(5), index=True, nullable=True), # Added country code
    Column("region", String(50), index=True, nullable=True), # Added region
    Column("is_active", Boolean, default=True, nullable=False), # Flag to enable/disable probing for this hub
    Column("source", String(50), nullable=True), # How was this hub identified? 'manual', 'probe_result'
    Column("created_at", DateTime, default=func.now(), nullable=False),
    Column("updated_at", DateTime, default=func.now(), onupdate=func.now(), nullable=False),
)

# 用户搜索记录表定义
user_searches_table = Table(
    "user_searches",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=False),
    Column("from_location", String(255), nullable=False),
    Column("to_location", String(255), nullable=False),
    Column("date", String(10), nullable=True),  # 格式：YYYY-MM-DD
    Column("passengers", Integer, default=1, nullable=False),
    Column("searched_at", DateTime, default=func.now(), nullable=False),
    Column("created_at", DateTime, default=func.now(), nullable=False),
)

# You can add more tables here as needed following the same pattern.

# 法律文本表定义
legal_texts_table = Table(
    "legal_texts",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("type", String(50), nullable=False, index=True),  # 文本类型（如disclaimer, risk_confirmation等）
    Column("subtype", String(50), nullable=True, index=True),  # 子类型（如a-b, a-b-x等）
    Column("content", Text, nullable=True),  # 文本内容（HTML格式）
    Column("version", String(20), nullable=False),  # 版本号
    Column("created_at", DateTime, default=func.now(), nullable=False),
    Column("updated_at", DateTime, default=func.now(), onupdate=func.now(), nullable=False),
    Column("is_active", Boolean, default=True, nullable=False),
    Column("language", String(10), nullable=False, default="zh-CN"),  # 语言代码
    Column("content_path", String(255), nullable=True),  # 可选，指向文件系统中的文件路径
)