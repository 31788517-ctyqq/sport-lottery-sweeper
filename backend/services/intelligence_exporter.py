"""
情报数据导出器
提供灵活、高效的情报数据导出功能，支持多种格式和自定义配置
"""
import csv
import json
import io
import pandas as pd
from datetime import datetime, date
from typing import List, Dict, Any, Optional, Union, BinaryIO
from enum import Enum
from dataclasses import dataclass, asdict
from pathlib import Path
import zipfile
import tempfile
import logging

from sqlalchemy.orm import Session, Query
from sqlalchemy import desc, asc

from ..models.intelligence import (
    Intelligence, IntelligenceType, IntelligenceSource, IntelligenceAnalytics,
    ConfidenceLevelEnum, ImportanceLevelEnum
)
from ..models.match import Match
from ..models.team import Team
from ..models.player import Player


class ExportFormat(Enum):
    """导出格式枚举"""
    CSV = "csv"
    JSON = "json"
    EXCEL = "excel"
    XML = "xml"
    HTML = "html"
    PDF = "pdf"  # 需要额外依赖


class ExportCompression(Enum):
    """导出压缩格式枚举"""
    NONE = "none"
    ZIP = "zip"
    GZIP = "gzip"


@dataclass
class ExportConfig:
    """导出配置"""
    format: ExportFormat = ExportFormat.CSV
    include_fields: Optional[List[str]] = None
    exclude_fields: Optional[List[str]] = None
    field_mappings: Optional[Dict[str, str]] = None
    compression: ExportCompression = ExportCompression.NONE
    include_metadata: bool = True
    chunk_size: int = 1000
    date_format: str = "%Y-%m-%d %H:%M:%S"
    timezone: str = "UTC"
    encoding: str = "utf-8"
    delimiter: str = ","  # CSV分隔符
    pretty_print: bool = True  # JSON/XML美化输出


@dataclass
class ExportResult:
    """导出结果"""
    success: bool
    format: str
    filename: str
    file_size: int
    record_count: int
    export_time: float
    compression_ratio: Optional[float] = None
    error_message: Optional[str] = None
    download_url: Optional[str] = None
    checksum: Optional[str] = None


class IntelligenceExporter:
    """
    情报数据导出器
    提供高级导出功能，支持批量处理、格式转换和压缩
    """
    
    # 默认字段映射
    DEFAULT_FIELD_MAPPINGS = {
        "id": "ID",
        "match_id": "比赛ID",
        "type_info.name": "情报类型",
        "source_info.name": "信息来源",
        "title": "标题",
        "content": "内容",
        "summary": "摘要",
        "confidence": "置信度",
        "confidence_score": "置信度分数",
        "importance": "重要性",
        "base_weight": "基础权重",
        "calculated_weight": "计算权重",
        "status": "状态",
        "is_verified": "是否已验证",
        "published_at": "发布时间",
        "created_at": "创建时间",
        "updated_at": "更新时间",
        "view_count": "浏览量",
        "like_count": "点赞数",
        "comment_count": "评论数",
        "share_count": "分享数",
        "popularity_score": "热门度得分"
    }
    
    # 支持的格式
    SUPPORTED_FORMATS = {
        ExportFormat.CSV: [".csv"],
        ExportFormat.JSON: [".json"],
        ExportFormat.EXCEL: [".xlsx", ".xls"],
        ExportFormat.XML: [".xml"],
        ExportFormat.HTML: [".html"],
        ExportFormat.PDF: [".pdf"]
    }
    
    def __init__(self, db_session: Session, logger: Optional[logging.Logger] = None):
        """
        初始化导出器
        
        Args:
            db_session: 数据库会话
            logger: 日志记录器
        """
        self.db = db_session
        self.logger = logger or logging.getLogger(__name__)
    
    def export_intelligence(self, query: Optional[Query] = None, 
                          config: Optional[ExportConfig] = None) -> ExportResult:
        """
        导出情报数据
        
        Args:
            query: 查询对象，如果为None则导出所有数据
            config: 导出配置
            
        Returns:
            ExportResult: 导出结果
        """
        start_time = datetime.utcnow()
        
        try:
            # 使用默认配置
            if config is None:
                config = ExportConfig()
            
            # 准备查询
            if query is None:
                query = self.db.query(Intelligence).order_by(desc(Intelligence.created_at))
            
            # 获取数据
            intelligence_list = query.all()
            
            if not intelligence_list:
                return ExportResult(
                    success=True,
                    format=config.format.value,
                    filename=f"intelligence_export_{start_time.strftime('%Y%m%d_%H%M%S')}.{config.format.value}",
                    file_size=0,
                    record_count=0,
                    export_time=0.0,
                    error_message="没有数据可导出"
                )
            
            # 根据格式导出
            if config.format == ExportFormat.CSV:
                result = self._export_csv(intelligence_list, config)
            elif config.format == ExportFormat.JSON:
                result = self._export_json(intelligence_list, config)
            elif config.format == ExportFormat.EXCEL:
                result = self._export_excel(intelligence_list, config)
            elif config.format == ExportFormat.XML:
                result = self._export_xml(intelligence_list, config)
            elif config.format == ExportFormat.HTML:
                result = self._export_html(intelligence_list, config)
            elif config.format == ExportFormat.PDF:
                result = self._export_pdf(intelligence_list, config)
            else:
                raise ValueError(f"不支持的导出格式: {config.format}")
            
            # 计算导出时间
            export_time = (datetime.utcnow() - start_time).total_seconds()
            
            # 应用压缩
            if config.compression != ExportCompression.NONE:
                result = self._apply_compression(result, config)
            
            # 构建最终结果
            return ExportResult(
                success=True,
                format=config.format.value,
                filename=result["filename"],
                file_size=result["size"],
                record_count=len(intelligence_list),
                export_time=export_time,
                compression_ratio=result.get("compression_ratio"),
                download_url=result.get("download_url"),
                checksum=result.get("checksum")
            )
            
        except Exception as e:
            self.logger.error(f"导出失败: {str(e)}", exc_info=True)
            export_time = (datetime.utcnow() - start_time).total_seconds()
            
            return ExportResult(
                success=False,
                format=config.format.value if config else "unknown",
                filename="",
                file_size=0,
                record_count=0,
                export_time=export_time,
                error_message=str(e)
            )
    
    def export_by_criteria(self, filters: Dict[str, Any], config: Optional[ExportConfig] = None) -> ExportResult:
        """
        根据条件导出情报数据
        
        Args:
            filters: 筛选条件字典
            config: 导出配置
            
        Returns:
            ExportResult: 导出结果
        """
        try:
            # 构建查询
            query = self.db.query(Intelligence)
            
            # 应用筛选条件
            if "match_id" in filters:
                query = query.filter(Intelligence.match_id == filters["match_id"])
            
            if "type_id" in filters:
                query = query.filter(Intelligence.type_id == filters["type_id"])
            
            if "source_id" in filters:
                query = query.filter(Intelligence.source_id == filters["source_id"])
            
            if "status" in filters:
                query = query.filter(Intelligence.status == filters["status"])
            
            if "is_verified" in filters:
                query = query.filter(Intelligence.is_verified == filters["is_verified"])
            
            if "date_from" in filters:
                query = query.filter(Intelligence.created_at >= filters["date_from"])
            
            if "date_to" in filters:
                query = query.filter(Intelligence.created_at <= filters["date_to"])
            
            if "min_weight" in filters:
                query = query.filter(Intelligence.calculated_weight >= filters["min_weight"])
            
            if "max_weight" in filters:
                query = query.filter(Intelligence.calculated_weight <= filters["max_weight"])
            
            # 排序
            sort_field = filters.get("sort_field", "created_at")
            sort_order = filters.get("sort_order", "desc")
            
            if sort_order == "asc":
                query = query.order_by(asc(getattr(Intelligence, sort_field, "created_at")))
            else:
                query = query.order_by(desc(getattr(Intelligence, sort_field, "created_at")))
            
            # 执行导出
            return self.export_intelligence(query, config)
            
        except Exception as e:
            self.logger.error(f"按条件导出失败: {str(e)}", exc_info=True)
            return ExportResult(
                success=False,
                format=config.format.value if config else "unknown",
                filename="",
                file_size=0,
                record_count=0,
                export_time=0.0,
                error_message=str(e)
            )
    
    def export_statistics_report(self, days: int = 30, config: Optional[ExportConfig] = None) -> ExportResult:
        """
        导出统计报告
        
        Args:
            days: 统计天数
            config: 导出配置
            
        Returns:
            ExportResult: 导出结果
        """
        try:
            # 计算日期范围
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # 获取统计数据
            stats = self._calculate_statistics(start_date, end_date)
            
            # 生成报告数据
            report_data = self._generate_report_data(stats, days)
            
            # 导出报告
            if config is None:
                config = ExportConfig(format=ExportFormat.EXCEL)
            
            if config.format == ExportFormat.EXCEL:
                result = self._export_excel_report(report_data, config)
            elif config.format == ExportFormat.HTML:
                result = self._export_html_report(report_data, config)
            elif config.format == ExportFormat.PDF:
                result = self._export_pdf_report(report_data, config)
            else:
                # 默认使用JSON
                result = self._export_json_report(report_data, config)
            
            return ExportResult(
                success=True,
                format=config.format.value,
                filename=result["filename"],
                file_size=result["size"],
                record_count=len(report_data.get("sections", [])),
                export_time=result.get("export_time", 0.0),
                download_url=result.get("download_url")
            )
            
        except Exception as e:
            self.logger.error(f"导出统计报告失败: {str(e)}", exc_info=True)
            return ExportResult(
                success=False,
                format=config.format.value if config else "unknown",
                filename="",
                file_size=0,
                record_count=0,
                export_time=0.0,
                error_message=str(e)
            )
    
    def batch_export(self, export_tasks: List[Dict[str, Any]]) -> List[ExportResult]:
        """
        批量导出任务
        
        Args:
            export_tasks: 导出任务列表
            
        Returns:
            List[ExportResult]: 导出结果列表
        """
        results = []
        
        for i, task in enumerate(export_tasks):
            self.logger.info(f"开始执行导出任务 {i+1}/{len(export_tasks)}")
            
            try:
                filters = task.get("filters", {})
                config_dict = task.get("config", {})
                
                # 转换配置
                config = None
                if config_dict:
                    config = ExportConfig(**config_dict)
                
                # 执行导出
                result = self.export_by_criteria(filters, config)
                results.append(result)
                
                self.logger.info(f"导出任务 {i+1} 完成: {result.success}")
                
            except Exception as e:
                self.logger.error(f"导出任务 {i+1} 失败: {str(e)}")
                results.append(ExportResult(
                    success=False,
                    format=task.get("config", {}).get("format", "unknown"),
                    filename="",
                    file_size=0,
                    record_count=0,
                    export_time=0.0,
                    error_message=str(e)
                ))
        
        return results
    
    def get_export_templates(self) -> Dict[str, Any]:
        """
        获取导出模板
        
        Returns:
            Dict[str, Any]: 模板信息
        """
        return {
            "templates": [
                {
                    "name": "基础情报导出",
                    "description": "导出所有基础情报字段",
                    "config": {
                        "format": "csv",
                        "include_fields": ["id", "match_id", "title", "content", "confidence", "importance", "calculated_weight", "created_at"],
                        "compression": "none"
                    }
                },
                {
                    "name": "详细情报报告",
                    "description": "包含所有字段的详细报告",
                    "config": {
                        "format": "excel",
                        "include_fields": None,  # 包含所有字段
                        "compression": "zip"
                    }
                },
                {
                    "name": "统计摘要",
                    "description": "按天统计的摘要报告",
                    "config": {
                        "format": "json",
                        "include_metadata": True,
                        "pretty_print": True
                    }
                },
                {
                    "name": "高风险情报",
                    "description": "导出低置信度高重要性的情报",
                    "filters": {
                        "min_weight": 0.7,
                        "confidence": ["high", "very_high", "confirmed"]
                    },
                    "config": {
                        "format": "csv",
                        "field_mappings": {
                            "id": "ID",
                            "title": "标题",
                            "confidence": "置信度",
                            "importance": "重要性",
                            "calculated_weight": "风险权重",
                            "source_info.name": "信息来源"
                        }
                    }
                }
            ],
            "supported_formats": [fmt.value for fmt in ExportFormat],
            "default_config": asdict(ExportConfig())
        }
    
    def _export_csv(self, intelligence_list: List[Intelligence], config: ExportConfig) -> Dict[str, Any]:
        """导出为CSV格式"""
        output = io.StringIO()
        
        # 确定字段列表
        fieldnames = self._get_fieldnames(intelligence_list, config)
        
        # 创建CSV写入器
        writer = csv.DictWriter(output, fieldnames=fieldnames, delimiter=config.delimiter)
        writer.writeheader()
        
        # 写入数据
        for intel in intelligence_list:
            row = self._create_data_row(intel, fieldnames, config)
            writer.writerow(row)
        
        csv_data = output.getvalue()
        output.close()
        
        # 生成文件名
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"intelligence_export_{timestamp}.csv"
        
        return {
            "format": "csv",
            "data": csv_data,
            "filename": filename,
            "size": len(csv_data.encode(config.encoding)),
            "encoding": config.encoding
        }
    
    def _export_json(self, intelligence_list: List[Intelligence], config: ExportConfig) -> Dict[str, Any]:
        """导出为JSON格式"""
        # 准备数据
        json_data = []
        for intel in intelligence_list:
            item = self._create_json_item(intel, config)
            json_data.append(item)
        
        # 添加元数据
        if config.include_metadata:
            result = {
                "metadata": {
                    "export_time": datetime.utcnow().isoformat(),
                    "record_count": len(json_data),
                    "format": "json",
                    "version": "1.0"
                },
                "data": json_data
            }
        else:
            result = json_data
        
        # 序列化
        if config.pretty_print:
            json_str = json.dumps(result, ensure_ascii=False, indent=2, default=self._json_serializer)
        else:
            json_str = json.dumps(result, ensure_ascii=False, default=self._json_serializer)
        
        # 生成文件名
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"intelligence_export_{timestamp}.json"
        
        return {
            "format": "json",
            "data": json_str,
            "filename": filename,
            "size": len(json_str.encode(config.encoding)),
            "encoding": config.encoding
        }
    
    def _export_excel(self, intelligence_list: List[Intelligence], config: ExportConfig) -> Dict[str, Any]:
        """导出为Excel格式"""
        try:
            # 准备数据
            data = []
            for intel in intelligence_list:
                row = self._create_excel_row(intel, config)
                data.append(row)
            
            # 创建DataFrame
            fieldnames = self._get_fieldnames(intelligence_list, config)
            df = pd.DataFrame(data, columns=fieldnames)
            
            # 写入Excel
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Intelligence', index=False)
                
                # 添加摘要工作表
                self._add_summary_sheet(writer, intelligence_list)
            
            excel_data = output.getvalue()
            output.close()
            
            # 生成文件名
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"intelligence_export_{timestamp}.xlsx"
            
            return {
                "format": "excel",
                "data": excel_data,
                "filename": filename,
                "size": len(excel_data),
                "encoding": "binary"
            }
            
        except ImportError:
            self.logger.warning("openpyxl未安装，无法导出Excel格式")
            raise ValueError("Excel导出需要openpyxl库，请先安装: pip install openpyxl")
    
    def _export_xml(self, intelligence_list: List[Intelligence], config: ExportConfig) -> Dict[str, Any]:
        """导出为XML格式"""
        import xml.etree.ElementTree as ET
        from xml.dom import minidom
        
        # 创建根元素
        root = ET.Element("intelligence_export")
        
        # 添加元数据
        if config.include_metadata:
            metadata = ET.SubElement(root, "metadata")
            ET.SubElement(metadata, "export_time").text = datetime.utcnow().isoformat()
            ET.SubElement(metadata, "record_count").text = str(len(intelligence_list))
            ET.SubElement(metadata, "format").text = "xml"
            ET.SubElement(metadata, "version").text = "1.0"
        
        # 添加数据
        data_elem = ET.SubElement(root, "data")
        for intel in intelligence_list:
            item_elem = ET.SubElement(data_elem, "item")
            item_data = self._create_xml_item(intel, config)
            
            for key, value in item_data.items():
                if value is not None:
                    elem = ET.SubElement(item_elem, key)
                    elem.text = str(value)
        
        # 生成XML字符串
        rough_string = ET.tostring(root, encoding=config.encoding)
        
        if config.pretty_print:
            parsed = minidom.parseString(rough_string)
            xml_str = parsed.toprettyxml(indent="  ", encoding=config.encoding)
        else:
            xml_str = rough_string
        
        # 生成文件名
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"intelligence_export_{timestamp}.xml"
        
        return {
            "format": "xml",
            "data": xml_str.decode(config.encoding) if isinstance(xml_str, bytes) else xml_str,
            "filename": filename,
            "size": len(xml_str),
            "encoding": config.encoding
        }
    
    def _export_html(self, intelligence_list: List[Intelligence], config: ExportConfig) -> Dict[str, Any]:
        """导出为HTML格式"""
        # 生成HTML表格
        html = ['<!DOCTYPE html>', '<html>', '<head>']
        html.append('<meta charset="utf-8">')
        html.append('<title>情报数据导出</title>')
        html.append('<style>')
        html.append('table { border-collapse: collapse; width: 100%; }')
        html.append('th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }')
        html.append('th { background-color: #f2f2f2; font-weight: bold; }')
        html.append('tr:nth-child(even) { background-color: #f9f9f9; }')
        html.append('</style>')
        html.append('</head>')
        html.append('<body>')
        
        # 添加元数据
        if config.include_metadata:
            html.append('<h1>情报数据导出报告</h1>')
            html.append(f'<p>导出时间: {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")} UTC</p>')
            html.append(f'<p>记录数量: {len(intelligence_list)}</p>')
            html.append('<hr>')
        
        # 创建表格
        html.append('<table>')
        
        # 表头
        fieldnames = self._get_fieldnames(intelligence_list, config)
        html.append('<tr>')
        for field in fieldnames:
            html.append(f'<th>{field}</th>')
        html.append('</tr>')
        
        # 数据行
        for intel in intelligence_list:
            html.append('<tr>')
            row = self._create_data_row(intel, fieldnames, config)
            for field in fieldnames:
                value = row.get(field, '')
                html.append(f'<td>{value}</td>')
            html.append('</tr>')
        
        html.append('</table>')
        html.append('</body>')
        html.append('</html>')
        
        html_str = '\n'.join(html)
        
        # 生成文件名
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"intelligence_export_{timestamp}.html"
        
        return {
            "format": "html",
            "data": html_str,
            "filename": filename,
            "size": len(html_str.encode(config.encoding)),
            "encoding": config.encoding
        }
    
    def _export_pdf(self, intelligence_list: List[Intelligence], config: ExportConfig) -> Dict[str, Any]:
        """导出为PDF格式"""
        # 注意：PDF导出需要额外的依赖
        self.logger.warning("PDF导出功能需要额外依赖，当前返回占位符")
        
        # 生成简单的文本PDF（实际应用中可使用reportlab等库）
        pdf_content = f"""情报数据导出报告
导出时间: {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")}
记录数量: {len(intelligence_list)}

数据摘要:
"""
        
        for intel in intelligence_list[:10]:  # 只显示前10条
            pdf_content += f"- {intel.title}: 权重 {intel.calculated_weight:.2f}, 置信度 {intel.confidence.value}\n"
        
        if len(intelligence_list) > 10:
            pdf_content += f"\n... 以及另外 {len(intelligence_list) - 10} 条记录"
        
        # 生成文件名
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"intelligence_export_{timestamp}.pdf"
        
        return {
            "format": "pdf",
            "data": pdf_content,
            "filename": filename,
            "size": len(pdf_content.encode(config.encoding)),
            "encoding": config.encoding,
            "note": "这是一个简化的PDF导出，实际应用中需要安装PDF生成库"
        }
    
    def _apply_compression(self, export_result: Dict[str, Any], config: ExportConfig) -> Dict[str, Any]:
        """应用压缩"""
        if config.compression == ExportCompression.NONE:
            return export_result
        
        try:
            data = export_result["data"]
            if isinstance(data, str):
                data = data.encode(export_result.get("encoding", "utf-8"))
            
            if config.compression == ExportCompression.ZIP:
                # 创建ZIP文件
                import zipfile
                import tempfile
                
                with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_file:
                    with zipfile.ZipFile(tmp_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                        zipf.writestr(export_result["filename"], data)
                    
                    # 读取压缩后的数据
                    tmp_file.seek(0)
                    compressed_data = tmp_file.read()
                
                # 计算压缩比
                original_size = export_result["size"]
                compressed_size = len(compressed_data)
                compression_ratio = compressed_size / original_size if original_size > 0 else 0
                
                # 更新结果
                export_result.update({
                    "data": compressed_data,
                    "size": compressed_size,
                    "filename": f"{export_result['filename']}.zip",
                    "compression_ratio": round(compression_ratio, 3),
                    "encoding": "binary"
                })
            
            elif config.compression == ExportCompression.GZIP:
                # GZIP压缩
                import gzip
                
                compressed_data = gzip.compress(data)
                compression_ratio = len(compressed_data) / len(data) if len(data) > 0 else 0
                
                export_result.update({
                    "data": compressed_data,
                    "size": len(compressed_data),
                    "filename": f"{export_result['filename']}.gz",
                    "compression_ratio": round(compression_ratio, 3),
                    "encoding": "binary"
                })
            
            return export_result
            
        except Exception as e:
            self.logger.error(f"压缩失败: {str(e)}")
            return export_result  # 返回未压缩的结果
    
    def _get_fieldnames(self, intelligence_list: List[Intelligence], config: ExportConfig) -> List[str]:
        """获取字段名列表"""
        # 如果有指定包含字段，使用指定字段
        if config.include_fields:
            fieldnames = config.include_fields
        else:
            # 使用默认字段
            fieldnames = list(self.DEFAULT_FIELD_MAPPINGS.keys())
            
            # 如果有排除字段，移除它们
            if config.exclude_fields:
                fieldnames = [f for f in fieldnames if f not in config.exclude_fields]
        
        # 应用字段映射
        if config.field_mappings:
            # 重新映射字段名（显示名称）
            mapped_fieldnames = []
            for field in fieldnames:
                mapped_fieldnames.append(config.field_mappings.get(field, field))
            return mapped_fieldnames
        
        return fieldnames
    
    def _create_data_row(self, intelligence: Intelligence, fieldnames: List[str], config: ExportConfig) -> Dict[str, Any]:
        """创建数据行"""
        row = {}
        
        for field in fieldnames:
            # 反向查找原始字段名
            original_field = field
            if config.field_mappings:
                for orig, mapped in config.field_mappings.items():
                    if mapped == field:
                        original_field = orig
                        break
            
            # 获取字段值
            value = self._get_field_value(intelligence, original_field)
            
            # 格式化值
            if isinstance(value, datetime):
                value = value.strftime(config.date_format)
            elif isinstance(value, date):
                value = value.strftime("%Y-%m-%d")
            elif isinstance(value, (ConfidenceLevelEnum, ImportanceLevelEnum)):
                value = value.value
            elif isinstance(value, bool):
                value = "是" if value else "否"
            elif value is None:
                value = ""
            
            row[field] = value
        
        return row
    
    def _get_field_value(self, intelligence: Intelligence, field: str) -> Any:
        """获取字段值，支持嵌套属性"""
        if '.' in field:
            # 处理嵌套属性，如 "type_info.name"
            parts = field.split('.')
            obj = intelligence
            for part in parts:
                if hasattr(obj, part):
                    obj = getattr(obj, part)
                else:
                    return None
            return obj
        else:
            # 直接属性
            return getattr(intelligence, field, None)
    
    def _create_json_item(self, intelligence: Intelligence, config: ExportConfig) -> Dict[str, Any]:
        """创建JSON数据项"""
        item = {}
        fieldnames = self._get_fieldnames([intelligence], config)
        
        for field in fieldnames:
            original_field = field
            if config.field_mappings:
                for orig, mapped in config.field_mappings.items():
                    if mapped == field:
                        original_field = orig
                        break
            
            value = self._get_field_value(intelligence, original_field)
            item[field] = value
        
        return item
    
    def _json_serializer(self, obj):
        """JSON序列化器"""
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        elif isinstance(obj, (ConfidenceLevelEnum, ImportanceLevelEnum)):
            return obj.value
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        raise TypeError(f"Type {type(obj)} not serializable")
    
    def _create_excel_row(self, intelligence: Intelligence, config: ExportConfig) -> List[Any]:
        """创建Excel数据行"""
        row = []
        fieldnames = self._get_fieldnames([intelligence], config)
        
        for field in fieldnames:
            original_field = field
            if config.field_mappings:
                for orig, mapped in config.field_mappings.items():
                    if mapped == field:
                        original_field = orig
                        break
            
            value = self._get_field_value(intelligence, original_field)
            row.append(value)
        
        return row
    
    def _create_xml_item(self, intelligence: Intelligence, config: ExportConfig) -> Dict[str, Any]:
        """创建XML数据项"""
        item = {}
        fieldnames = self._get_fieldnames([intelligence], config)
        
        for field in fieldnames:
            original_field = field
            if config.field_mappings:
                for orig, mapped in config.field_mappings.items():
                    if mapped == field:
                        original_field = orig
                        break
            
            value = self._get_field_value(intelligence, original_field)
            
            # XML需要字符串值
            if isinstance(value, (datetime, date)):
                value = value.isoformat()
            elif isinstance(value, (ConfidenceLevelEnum, ImportanceLevelEnum)):
                value = value.value
            elif value is None:
                value = ""
            else:
                value = str(value)
            
            item[field] = value
        
        return item
    
    def _add_summary_sheet(self, writer, intelligence_list: List[Intelligence]):
        """添加摘要工作表"""
        summary_data = {
            "统计项目": ["总记录数", "平均权重", "已验证比例", "高置信度比例", "最新记录时间"],
            "数值": [
                len(intelligence_list),
                round(sum(i.calculated_weight for i in intelligence_list) / len(intelligence_list), 3),
                f"{sum(1 for i in intelligence_list if i.is_verified) / len(intelligence_list) * 100:.1f}%",
                f"{sum(1 for i in intelligence_list if i.confidence in [ConfidenceLevelEnum.HIGH, ConfidenceLevelEnum.VERY_HIGH, ConfidenceLevelEnum.CONFIRMED]) / len(intelligence_list) * 100:.1f}%",
                max(i.created_at for i in intelligence_list).strftime("%Y-%m-%d %H:%M") if intelligence_list else "N/A"
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='摘要', index=False)
    
    def _calculate_statistics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """计算统计数据"""
        # 获取数据
        intelligence_list = self.db.query(Intelligence).filter(
            Intelligence.created_at.between(start_date, end_date)
        ).all()
        
        if not intelligence_list:
            return {}
        
        # 计算基本统计
        total_count = len(intelligence_list)
        verified_count = sum(1 for i in intelligence_list if i.is_verified)
        high_confidence_count = sum(1 for i in intelligence_list if i.confidence in [ConfidenceLevelEnum.HIGH, ConfidenceLevelEnum.VERY_HIGH, ConfidenceLevelEnum.CONFIRMED])
        high_importance_count = sum(1 for i in intelligence_list if i.importance in [ImportanceLevelEnum.HIGH, ImportanceLevelEnum.CRITICAL])
        
        avg_weight = sum(i.calculated_weight for i in intelligence_list) / total_count
        avg_popularity = sum(i.popularity_score for i in intelligence_list) / total_count
        
        # 按类型统计
        type_stats = {}
        for i in intelligence_list:
            if i.type_info:
                type_name = i.type_info.name
                type_stats[type_name] = type_stats.get(type_name, 0) + 1
        
        # 按来源统计
        source_stats = {}
        for i in intelligence_list:
            if i.source_info:
                source_name = i.source_info.name
                source_stats[source_name] = source_stats.get(source_name, 0) + 1
        
        return {
            "period": {
                "start": start_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d")
            },
            "total_count": total_count,
            "verified_count": verified_count,
            "verified_rate": verified_count / total_count * 100,
            "high_confidence_count": high_confidence_count,
            "high_confidence_rate": high_confidence_count / total_count * 100,
            "high_importance_count": high_importance_count,
            "high_importance_rate": high_importance_count / total_count * 100,
            "average_weight": avg_weight,
            "average_popularity": avg_popularity,
            "type_distribution": type_stats,
            "source_distribution": source_stats,
            "daily_counts": self._calculate_daily_counts(start_date, end_date)
        }
    
    def _calculate_daily_counts(self, start_date: datetime, end_date: datetime) -> Dict[str, int]:
        """计算每日计数"""
        daily_counts = {}
        current_date = start_date
        
        while current_date <= end_date:
            next_date = current_date + timedelta(days=1)
            count = self.db.query(Intelligence).filter(
                Intelligence.created_at.between(current_date, next_date)
            ).count()
            
            daily_counts[current_date.strftime("%Y-%m-%d")] = count
            current_date = next_date
        
        return daily_counts
    
    def _generate_report_data(self, stats: Dict[str, Any], days: int) -> Dict[str, Any]:
        """生成报告数据"""
        return {
            "report_title": f"情报数据统计报告（最近{days}天）",
            "generated_at": datetime.utcnow().isoformat(),
            "period": stats.get("period", {}),
            "summary": {
                "total_records": stats.get("total_count", 0),
                "verified_rate": round(stats.get("verified_rate", 0), 1),
                "high_confidence_rate": round(stats.get("high_confidence_rate", 0), 1),
                "average_quality_score": round(stats.get("average_weight", 0) * 100, 1)
            },
            "distributions": {
                "by_type": stats.get("type_distribution", {}),
                "by_source": stats.get("source_distribution", {}),
                "daily": stats.get("daily_counts", {})
            },
            "recommendations": self._generate_statistical_recommendations(stats)
        }
    
    def _generate_statistical_recommendations(self, stats: Dict[str, Any]) -> List[str]:
        """生成统计建议"""
        recommendations = []
        
        if stats.get("verified_rate", 0) < 50:
            recommendations.append("情报验证率较低，建议加强数据验证流程")
        
        if stats.get("high_confidence_rate", 0) < 60:
            recommendations.append("高置信度情报比例不足，建议优化数据源选择")
        
        if stats.get("average_weight", 0) < 0.6:
            recommendations.append("平均情报权重偏低，建议提高数据质量")
        
        # 检查数据分布
        type_dist = stats.get("type_distribution", {})
        if len(type_dist) < 5:
            recommendations.append("情报类型分布较窄，建议增加数据采集多样性")
        
        return recommendations
    
    def _export_excel_report(self, report_data: Dict[str, Any], config: ExportConfig) -> Dict[str, Any]:
        """导出Excel报告"""
        try:
            output = io.BytesIO()
            
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                # 摘要工作表
                summary_df = pd.DataFrame([report_data["summary"]])
                summary_df.to_excel(writer, sheet_name='摘要', index=False)
                
                # 类型分布
                if report_data["distributions"]["by_type"]:
                    type_df = pd.DataFrame(list(report_data["distributions"]["by_type"].items()), 
                                          columns=['类型', '数量'])
                    type_df.to_excel(writer, sheet_name='类型分布', index=False)
                
                # 来源分布
                if report_data["distributions"]["by_source"]:
                    source_df = pd.DataFrame(list(report_data["distributions"]["by_source"].items()), 
                                            columns=['来源', '数量'])
                    source_df.to_excel(writer, sheet_name='来源分布', index=False)
                
                # 每日计数
                if report_data["distributions"]["daily"]:
                    daily_df = pd.DataFrame(list(report_data["distributions"]["daily"].items()), 
                                           columns=['日期', '数量'])
                    daily_df.to_excel(writer, sheet_name='每日趋势', index=False)
            
            excel_data = output.getvalue()
            output.close()
            
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"intelligence_report_{timestamp}.xlsx"
            
            return {
                "data": excel_data,
                "filename": filename,
                "size": len(excel_data),
                "encoding": "binary",
                "export_time": 0.0
            }
            
        except Exception as e:
            self.logger.error(f"导出Excel报告失败: {str(e)}")
            raise
    
    def _export_json_report(self, report_data: Dict[str, Any], config: ExportConfig) -> Dict[str, Any]:
        """导出JSON报告"""
        json_str = json.dumps(report_data, ensure_ascii=False, indent=2, default=self._json_serializer)
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"intelligence_report_{timestamp}.json"
        
        return {
            "data": json_str,
            "filename": filename,
            "size": len(json_str.encode(config.encoding)),
            "encoding": config.encoding,
            "export_time": 0.0
        }
    
    def _export_html_report(self, report_data: Dict[str, Any], config: ExportConfig) -> Dict[str, Any]:
        """导出HTML报告"""
        html = ['<!DOCTYPE html>', '<html>', '<head>']
        html.append('<meta charset="utf-8">')
        html.append(f'<title>{report_data["report_title"]}</title>')
        html.append('<style>')
        html.append('body { font-family: Arial, sans-serif; margin: 20px; }')
        html.append('h1, h2 { color: #333; }')
        html.append('table { border-collapse: collapse; margin: 20px 0; }')
        html.append('th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }')
        html.append('th { background-color: #f2f2f2; }')
        html.append('.summary { background-color: #f9f9f9; padding: 15px; border-radius: 5px; }')
        html.append('.recommendation { background-color: #fff3cd; border: 1px solid #ffeaa7; padding: 10px; margin: 10px 0; border-radius: 3px; }')
        html.append('</style>')
        html.append('</head>')
        html.append('<body>')
        
        # 标题
        html.append(f'<h1>{report_data["report_title"]}</h1>')
        html.append(f'<p>生成时间: {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")} UTC</p>')
        html.append(f'<p>统计周期: {report_data["period"]["start"]} 至 {report_data["period"]["end"]}</p>')
        
        # 摘要
        html.append('<div class="summary">')
        html.append('<h2>摘要</h2>')
        html.append(f'<p>总记录数: {report_data["summary"]["total_records"]}</p>')
        html.append(f'<p>验证率: {report_data["summary"]["verified_rate"]}%</p>')
        html.append(f'<p>高置信度比例: {report_data["summary"]["high_confidence_rate"]}%</p>')
        html.append(f'<p>平均质量得分: {report_data["summary"]["average_quality_score"]}/100</p>')
        html.append('</div>')
        
        # 建议
        if "recommendations" in report_data and report_data["recommendations"]:
            html.append('<h2>改进建议</h2>')
            for rec in report_data["recommendations"]:
                html.append(f'<div class="recommendation">✓ {rec}</div>')
        
        # 分布数据
        if report_data["distributions"]["by_type"]:
            html.append('<h2>类型分布</h2>')
            html.append('<table>')
            html.append('<tr><th>类型</th><th>数量</th></tr>')
            for type_name, count in report_data["distributions"]["by_type"].items():
                html.append(f'<tr><td>{type_name}</td><td>{count}</td></tr>')
            html.append('</table>')
        
        html.append('</body>')
        html.append('</html>')
        
        html_str = '\n'.join(html)
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"intelligence_report_{timestamp}.html"
        
        return {
            "data": html_str,
            "filename": filename,
            "size": len(html_str.encode(config.encoding)),
            "encoding": config.encoding,
            "export_time": 0.0
        }
    
    def _export_pdf_report(self, report_data: Dict[str, Any], config: ExportConfig) -> Dict[str, Any]:
        """导出PDF报告"""
        # 简化版本，实际应用中可使用reportlab
        self.logger.warning("PDF报告导出功能需要额外依赖，当前返回HTML版本")
        return self._export_html_report(report_data, config)