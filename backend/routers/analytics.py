from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import uuid
import logging
import random

# 配置日志
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/earnings", response_model=Dict[str, Any])
async def get_earnings_analysis():
    """
    获取收益分析数据，用于前端图表展示。
    """
    # 生成过去12个月的收益数据
    earnings_data = []
    base_date = datetime.now() - timedelta(days=365)
    
    for i in range(12):
        current_date = base_date + timedelta(days=i * 30)
        month_name = current_date.strftime("%b")
        
        # 模拟月度收益数据
        base_earnings = 50 + (i * 5)  # 增长趋势
        earnings_data.append({
            "month": month_name,
            "earnings": base_earnings + random.randint(-10, 20),
            "tasks": random.randint(15, 35),
            "average_reward": round(random.uniform(0.8, 2.5), 2)
        })
    
    # 计算总收益
    total_earnings = sum(item["earnings"] for item in earnings_data)
    total_tasks = sum(item["tasks"] for item in earnings_data)
    
    return {
        "data": earnings_data,
        "total_earnings": total_earnings,
        "total_tasks": total_tasks,
        "average_monthly_earnings": round(total_earnings / 12, 2),
        "source": "backend",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/real-time/metrics", response_model=Dict[str, Any])
async def get_real_time_metrics():
    """
    获取实时指标数据，用于前端实时监控。
    """
    # 模拟实时任务执行数据
    active_executions = []
    for i in range(random.randint(2, 5)):
        execution = {
            "taskId": f"task_{uuid.uuid4().hex[:6]}",
            "title": f"Task {i+1}: {random.choice(['Data Analysis', 'Text Generation', 'Image Processing', 'Code Review'])}",
            "agent": f"Agent-{random.randint(1, 10)}",
            "progress": random.randint(10, 95),
            "currentStep": random.choice(["Initializing", "Processing", "Validating", "Finalizing"]),
            "estimatedCompletion": (datetime.now() + timedelta(minutes=random.randint(5, 60))).isoformat()
        }
        active_executions.append(execution)
    
    # 队列指标
    queue_metrics = {
        "totalInQueue": random.randint(5, 25),
        "avgWaitTime": random.randint(30, 300),  # seconds
        "throughputPerHour": random.randint(15, 45),
        "peakHours": ["09:00-11:00", "14:00-16:00"],
        "systemLoad": random.uniform(45, 85)  # percentage
    }
    
    # 系统性能指标
    system_metrics = {
        "cpuUsage": random.uniform(20, 70),
        "memoryUsage": random.uniform(40, 80),
        "networkLatency": random.uniform(10, 100),  # ms
        "activeConnections": random.randint(50, 200)
    }
    
    return {
        "data": {
            "activeExecutions": active_executions,
            "queueMetrics": queue_metrics,
            "systemMetrics": system_metrics,
            "lastUpdate": datetime.now().isoformat()
        },
        "source": "backend",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/network-activity", response_model=Dict[str, Any])
async def get_network_activity_heatmap():
    """
    获取网络活动热力图数据。
    """
    # 生成24小时x7天的热力图数据
    heatmap_data = []
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    
    for day_idx, day in enumerate(days):
        for hour in range(24):
            # 工作日和工作时间有更高的活动
            is_workday = day_idx < 5
            is_work_hour = 9 <= hour <= 17
            
            base_activity = 30
            if is_workday and is_work_hour:
                base_activity = 80
            elif is_workday:
                base_activity = 40
            elif is_work_hour:
                base_activity = 50
            
            activity_level = base_activity + random.randint(-15, 20)
            
            heatmap_data.append({
                "day": day,
                "hour": hour,
                "activity": max(0, min(100, activity_level)),
                "tasks": random.randint(0, 15) if activity_level > 20 else 0
            })
    
    return {
        "data": heatmap_data,
        "peak_activity": {
            "day": "Wed",
            "hour": 14,
            "level": 95
        },
        "source": "backend",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/quality-metrics", response_model=Dict[str, Any])
async def get_quality_metrics():
    """
    获取质量评估指标。
    """
    # 质量指标数据
    quality_data = {
        "overall_score": random.uniform(85, 95),
        "task_completion_rate": random.uniform(92, 98),
        "customer_satisfaction": random.uniform(88, 96),
        "error_rate": random.uniform(1, 5),
        "response_time_score": random.uniform(85, 95),
        "accuracy_score": random.uniform(90, 98)
    }
    
    # 质量趋势（过去7天）
    trend_data = []
    for i in range(7):
        date = (datetime.now() - timedelta(days=6-i)).strftime("%Y-%m-%d")
        trend_data.append({
            "date": date,
            "quality_score": random.uniform(80, 95),
            "tasks_completed": random.randint(20, 50)
        })
    
    return {
        "current_metrics": quality_data,
        "trend_data": trend_data,
        "benchmarks": {
            "industry_average": 82.5,
            "target_score": 90.0,
            "minimum_acceptable": 75.0
        },
        "source": "backend",
        "timestamp": datetime.now().isoformat()
    }

@router.get("/predictive", response_model=Dict[str, Any])
async def get_predictive_analytics():
    """
    获取预测分析数据。
    """
    # 预测数据（未来30天）
    predictions = []
    base_date = datetime.now()
    
    for i in range(30):
        future_date = base_date + timedelta(days=i)
        # 模拟预测：周末任务较少，月末任务增多
        is_weekend = future_date.weekday() >= 5
        is_month_end = future_date.day > 25
        
        base_tasks = 8
        if is_weekend:
            base_tasks = 3
        if is_month_end:
            base_tasks += 5
        
        predictions.append({
            "date": future_date.strftime("%Y-%m-%d"),
            "predicted_tasks": base_tasks + random.randint(-2, 4),
            "predicted_earnings": round((base_tasks * 0.15) + random.uniform(-0.5, 1.0), 2),
            "confidence": random.uniform(75, 95)
        })
    
    # 趋势分析
    trends = {
        "task_growth_rate": random.uniform(5, 15),  # percentage
        "earnings_projection": random.uniform(1200, 2500),  # next month
        "capacity_utilization": random.uniform(70, 90),
        "resource_demand": random.choice(["Low", "Medium", "High"])
    }
    
    return {
        "predictions": predictions,
        "trends": trends,
        "recommendations": [
            "Consider scaling up agent capacity during month-end periods",
            "Optimize task distribution for weekend efficiency",
            "Implement predictive maintenance for peak load periods"
        ],
        "source": "backend",
        "timestamp": datetime.now().isoformat()
    }