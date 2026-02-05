"""
PDF导出路由

提供分析报告的PDF导出功能
使用 reportlab 生成PDF
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
import logging
from io import BytesIO
from datetime import datetime
import re
from html import unescape

from storage.database import Database

router = APIRouter(prefix="/api/export", tags=["export"])
logger = logging.getLogger(__name__)


async def get_db():
    """依赖注入：数据库"""
    db = Database()
    await db.initialize()
    return db


def markdown_to_pdf_bytes(markdown_text: str, metadata: dict) -> BytesIO:
    """
    将Markdown转换为PDF字节流
    
    Args:
        markdown_text: Markdown文本
        metadata: 报告元数据
        
    Returns:
        PDF字节流
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, PageBreak, 
            Table, TableStyle, Preformatted, HRFlowable
        )
        from reportlab.lib import colors
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.lib.colors import HexColor
        import platform
    except ImportError:
        raise ImportError("reportlab not installed. Please install: pip install reportlab")
    
    # 注册中文字体
    system = platform.system()
    if system == 'Darwin':  # macOS
        try:
            pdfmetrics.registerFont(TTFont('STHeiti', '/System/Library/Fonts/STHeiti Medium.ttc', subfontIndex=0))
            pdfmetrics.registerFont(TTFont('Songti', '/System/Library/Fonts/Supplemental/Songti.ttc', subfontIndex=0))
            chinese_font = 'STHeiti'
            chinese_font_bold = 'STHeiti'
        except:
            logger.warning("无法加载系统中文字体，尝试使用默认字体")
            chinese_font = 'Helvetica'
            chinese_font_bold = 'Helvetica-Bold'
    elif system == 'Linux':
        try:
            # Linux常见中文字体路径
            pdfmetrics.registerFont(TTFont('NotoSansCJK', '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc', subfontIndex=0))
            chinese_font = 'NotoSansCJK'
            chinese_font_bold = 'NotoSansCJK'
        except:
            logger.warning("无法加载中文字体，尝试使用默认字体")
            chinese_font = 'Helvetica'
            chinese_font_bold = 'Helvetica-Bold'
    elif system == 'Windows':
        try:
            pdfmetrics.registerFont(TTFont('SimHei', 'C:\\Windows\\Fonts\\simhei.ttf'))
            pdfmetrics.registerFont(TTFont('SimSun', 'C:\\Windows\\Fonts\\simsun.ttc', subfontIndex=0))
            chinese_font = 'SimHei'
            chinese_font_bold = 'SimHei'
        except:
            logger.warning("无法加载中文字体，尝试使用默认字体")
            chinese_font = 'Helvetica'
            chinese_font_bold = 'Helvetica-Bold'
    else:
        chinese_font = 'Helvetica'
        chinese_font_bold = 'Helvetica-Bold'
    
    # 创建字节流
    buffer = BytesIO()
    
    # 创建PDF文档
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    # 创建样式
    styles = getSampleStyleSheet()
    
    # 标题样式
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=HexColor('#1a1a1a'),
        spaceAfter=12,
        alignment=TA_LEFT,
        fontName=chinese_font_bold
    )
    
    # H2样式
    h2_style = ParagraphStyle(
        'CustomH2',
        parent=styles['Heading2'],
        fontSize=18,
        textColor=HexColor('#1a1a1a'),
        spaceBefore=16,
        spaceAfter=8,
        fontName=chinese_font_bold
    )
    
    # H3样式
    h3_style = ParagraphStyle(
        'CustomH3',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=HexColor('#374151'),
        spaceBefore=12,
        spaceAfter=6,
        fontName=chinese_font_bold
    )
    
    # 正文样式
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=11,
        leading=16,
        textColor=HexColor('#333333'),
        alignment=TA_JUSTIFY,
        fontName=chinese_font
    )
    
    # 代码样式
    code_style = ParagraphStyle(
        'CustomCode',
        parent=styles['Code'],
        fontSize=9,
        textColor=HexColor('#dc2626'),
        backColor=HexColor('#f3f4f6'),
        fontName='Courier'
    )
    
    # 引用样式
    quote_style = ParagraphStyle(
        'CustomQuote',
        parent=styles['BodyText'],
        fontSize=11,
        leftIndent=20,
        textColor=HexColor('#1e40af'),
        backColor=HexColor('#f0f9ff'),
        borderColor=HexColor('#2563eb'),
        borderWidth=2,
        borderPadding=10,
        fontName=chinese_font
    )
    
    # 构建文档内容
    story = []
    
    # 添加元数据表格
    metadata_data = [
        ['分析类型', metadata.get('analysis_type', 'N/A')],
        ['生成时间', metadata.get('created_at', 'N/A')],
        ['LLM后端', metadata.get('llm_backend', 'N/A')],
    ]
    
    if metadata.get('llm_model'):
        metadata_data.append(['模型', metadata['llm_model']])
    if metadata.get('processing_time'):
        metadata_data.append(['处理时间', f"{metadata['processing_time']:.1f}秒"])
    if metadata.get('token_usage'):
        metadata_data.append(['Token使用', f"{metadata['token_usage']:,}"])
    if metadata.get('estimated_cost') is not None:
        metadata_data.append(['预估成本', f"${metadata['estimated_cost']:.4f}"])
    if metadata.get('article_count'):
        metadata_data.append(['文章数量', str(metadata['article_count'])])
    
    metadata_table = Table(metadata_data, colWidths=[4*cm, 13*cm])
    metadata_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), HexColor('#f3f4f6')),
        ('TEXTCOLOR', (0, 0), (-1, -1), HexColor('#1a1a1a')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), chinese_font_bold),
        ('FONTNAME', (1, 0), (1, -1), chinese_font),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#d1d5db')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    story.append(metadata_table)
    story.append(Spacer(1, 0.5*cm))
    
    # 解析Markdown并转换为PDF元素
    lines = markdown_text.split('\n')
    i = 0
    in_list = False
    list_items = []
    
    def flush_list():
        """输出累积的列表项"""
        nonlocal in_list, list_items
        if list_items:
            for item in list_items:
                story.append(item)
            list_items = []
        in_list = False
    
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        
        # 空行
        if not stripped:
            flush_list()
            story.append(Spacer(1, 0.3*cm))
            i += 1
            continue
        
        # 标题（必须在行首，清除列表）
        if stripped.startswith('# '):
            flush_list()
            text = stripped[2:].strip()
            story.append(Spacer(1, 0.2*cm))
            story.append(Paragraph(process_inline_markdown(text), title_style))
            story.append(Spacer(1, 0.2*cm))
        elif stripped.startswith('## '):
            flush_list()
            text = stripped[3:].strip()
            story.append(Spacer(1, 0.15*cm))
            story.append(Paragraph(process_inline_markdown(text), h2_style))
        elif stripped.startswith('### '):
            flush_list()
            text = stripped[4:].strip()
            story.append(Paragraph(process_inline_markdown(text), h3_style))
        elif stripped.startswith('#### '):
            flush_list()
            text = stripped[5:].strip()
            story.append(Paragraph(process_inline_markdown(text), h3_style))
        
        # 代码块
        elif stripped.startswith('```'):
            flush_list()
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i])
                i += 1
            if code_lines:
                code_text = '\n'.join(code_lines)
                # 使用Preformatted保持格式
                from reportlab.platypus import Preformatted
                story.append(Spacer(1, 0.2*cm))
                story.append(Preformatted(escape_html(code_text), code_style))
                story.append(Spacer(1, 0.2*cm))
        
        # 引用块
        elif stripped.startswith('>'):
            flush_list()
            quote_text = stripped[1:].strip()
            story.append(Paragraph(process_inline_markdown(quote_text), quote_style))
        
        # 无序列表
        elif stripped.startswith('- ') or stripped.startswith('* '):
            text = stripped[2:].strip()
            list_style = ParagraphStyle(
                'ListItem',
                parent=body_style,
                leftIndent=20,
                firstLineIndent=-15,
                spaceBefore=3,
                spaceAfter=3
            )
            list_items.append(Paragraph(f"• {process_inline_markdown(text)}", list_style))
            in_list = True
        
        # 有序列表
        elif re.match(r'^\d+\.\s', stripped):
            text = re.sub(r'^\d+\.\s', '', stripped)
            match = re.match(r'^(\d+)\.', stripped)
            num = match.group(1) if match else '1'
            list_style = ParagraphStyle(
                'OrderedListItem',
                parent=body_style,
                leftIndent=25,
                firstLineIndent=-20,
                spaceBefore=3,
                spaceAfter=3
            )
            list_items.append(Paragraph(f"{num}. {process_inline_markdown(text)}", list_style))
            in_list = True
        
        # 水平分割线
        elif stripped in ['---', '***', '___']:
            flush_list()
            from reportlab.platypus import HRFlowable
            story.append(Spacer(1, 0.3*cm))
            story.append(HRFlowable(width="100%", thickness=1, color=HexColor('#d1d5db')))
            story.append(Spacer(1, 0.3*cm))
        
        # 普通段落
        else:
            flush_list()
            # 处理粗体、斜体、行内代码
            text = process_inline_markdown(stripped)
            story.append(Paragraph(text, body_style))
        
        i += 1
    
    # 处理最后可能剩余的列表项
    flush_list()
    
    # 生成PDF
    doc.build(story)
    
    # 重置指针
    buffer.seek(0)
    return buffer


def escape_html(text: str) -> str:
    """转义HTML特殊字符"""
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    return text


def process_inline_markdown(text: str) -> str:
    """处理行内Markdown格式（粗体、斜体、代码）"""
    # 转义HTML
    text = escape_html(text)
    
    # 行内代码（先处理，避免被其他规则影响）
    text = re.sub(r'`([^`]+)`', r'<font face="Courier" color="#dc2626" backColor="#f3f4f6">\1</font>', text)
    
    # 粗体（先处理双星号，再处理下划线）
    text = re.sub(r'\*\*([^*]+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'__([^_]+?)__', r'<b>\1</b>', text)
    
    # 斜体（处理单星号和下划线，但不要匹配已处理的粗体）
    text = re.sub(r'(?<!\*)\*(?!\*)([^*]+?)(?<!\*)\*(?!\*)', r'<i>\1</i>', text)
    text = re.sub(r'(?<!_)_(?!_)([^_]+?)(?<!_)_(?!_)', r'<i>\1</i>', text)
    
    # 链接
    text = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<u><font color="#2563eb">\1</font></u>', text)
    
    # 删除线
    text = re.sub(r'~~([^~]+?)~~', r'<strike>\1</strike>', text)
    
    return text


@router.get("/analysis/{analysis_id}/pdf")
async def export_analysis_pdf(
    analysis_id: str,
    db: Database = Depends(get_db)
):
    """
    导出分析报告为PDF
    
    Args:
        analysis_id: 分析ID
        
    Returns:
        PDF文件下载响应
    """
    try:
        # 获取分析数据
        analysis = await db.get_analysis(analysis_id)
        
        if not analysis:
            raise HTTPException(
                status_code=404,
                detail=f"未找到分析 {analysis_id}"
            )
        
        if not analysis.markdown_report:
            raise HTTPException(
                status_code=400,
                detail="该分析没有Markdown报告，无法导出PDF"
            )
        
        # 准备元数据
        metadata = {
            'analysis_type': analysis.analysis_type.value,
            'created_at': analysis.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'llm_backend': analysis.llm_backend.upper(),
            'llm_model': analysis.llm_model,
            'processing_time': analysis.processing_time_seconds,
            'token_usage': analysis.token_usage,
            'estimated_cost': analysis.estimated_cost,
            'article_count': len(analysis.article_ids)
        }
        
        # 生成PDF
        try:
            pdf_bytes = markdown_to_pdf_bytes(analysis.markdown_report, metadata)
        except ImportError as e:
            raise HTTPException(
                status_code=500,
                detail=f"PDF生成库未安装: {str(e)}"
            )
        
        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"analysis_{analysis_id[:8]}_{timestamp}.pdf"
        
        logger.info(f"成功生成PDF: {filename}")
        
        # 返回PDF文件
        return StreamingResponse(
            pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"导出PDF失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"导出PDF失败: {str(e)}"
        )
