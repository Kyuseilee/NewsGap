# Gemini响应截断问题修复总结

## 问题描述

使用Gemini API进行分析时,文章在第三部分被截断,无法输出完整内容。

## 根本原因

1. **Gemini表格生成bug**: Gemini在生成Markdown表格时,会在单元格中填充大量空格(99.4%都是空格)
2. **输出字符数暴涨**: 原本应该几千字符的表格,被填充成197万字符
3. **触发token限制**: 虽然max_output_tokens设置为65536,但实际输出达到限制后被截断(finish_reason=2)
4. **空白占比极高**: 整体响应中88.2%是空白字符

## 解决方案

采用**多层防御**策略:

### 1. 通用格式约束 (prompts/base.yaml) ⭐️ 新增

在base.yaml中添加"格式规范"章节,作为**所有行业通用**的约束:

```yaml
## 4. 格式规范（重要）
- **使用简洁格式**：优先使用列表、分段等简洁格式组织内容
- **避免复杂表格**：不要使用包含大量列或复杂内容的Markdown表格
- **表格替代方案**：如需对比多个维度，使用层级列表或分段描述
- **控制输出长度**：避免重复、冗余内容，保持输出紧凑高效
- **完整性优先**：确保所有章节完整输出，不中途截断
```

**优势**:
- 所有行业(finance, tech, news, developer等)自动继承
- 统一管理,避免重复配置
- 新增行业自动生效

### 2. 提示词简化 (gemini_adapter.py:253-256)

简化用户提示词,避免重复:
```python
⚠️ **输出要求**：
- 直接输出 Markdown 格式，不要用代码块包裹
- 必须完整输出所有章节，确保包含结尾总结
```

### 3. Prompt模板优化 (prompts/templates/finance.yaml:110)

移除finance.yaml中的重复格式约束:
```yaml
### 资产配置建议

对以下资产类别给出明确的配置建议（增持/标配/减持/规避）：
```

之前的`⚠️ **格式要求**: 使用简洁的列表格式,避免使用复杂表格`已移至base.yaml。

### 4. 后处理清理 (gemini_adapter.py:95, 263-300)

添加`_clean_table_spaces()`函数,清理表格中的过量空格:
- 识别Markdown表格行(以`|`开头和结尾)
- 将连续4个以上空格压缩为3个
- 测试显示可节省99.7%的空间

```python
def _clean_table_spaces(self, text: str) -> str:
    """清理Markdown表格中的过量空格"""
    import re
    lines = text.split('\n')
    cleaned_lines = []
    
    for line in lines:
        if line.strip().startswith('|') and line.strip().endswith('|'):
            cells = line.split('|')
            cleaned_cells = []
            for cell in cells:
                cleaned_cell = re.sub(r' {4,}', '   ', cell)
                cleaned_cells.append(cleaned_cell)
            cleaned_line = '|'.join(cleaned_cells)
            cleaned_lines.append(cleaned_line)
        else:
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)
```

## 修改文件清单

1. `backend/prompts/base.yaml` ⭐️
   - 第5行: 将`system_prompt:`改为`system_prompt_base:`
   - 第29-38行: 新增"4. 格式规范"章节(通用约束)

2. `backend/llm/gemini_adapter.py`
   - 第95行: 添加表格空格清理调用
   - 第253-256行: 简化输出要求提示词
   - 第263-300行: 新增`_clean_table_spaces()`方法

3. `backend/prompts/templates/finance.yaml`
   - 第110-114行: 移除重复的格式要求,改为继承base.yaml

## 架构优势

### 之前:
```
finance.yaml → 格式约束(重复)
tech.yaml → 没有格式约束
news.yaml → 没有格式约束
...
```

### 现在:
```
base.yaml → 格式规范(统一)
    ↓ 继承
finance.yaml, tech.yaml, news.yaml, developer.yaml, ... (所有行业)
```

**好处**:
1. ✅ **DRY原则**: 不重复,统一管理
2. ✅ **全局生效**: 所有行业自动受益
3. ✅ **易于维护**: 只需修改base.yaml一处
4. ✅ **新增友好**: 新行业自动继承格式约束

## 预期效果

1. **防止表格生成**: 通过系统提示词引导模型使用列表而非表格
2. **清理冗余空格**: 即使生成了表格,也能自动清理多余空格
3. **完整输出**: 避免触发max_output_tokens限制,确保输出完整
4. **监控日志**: 在日志中记录清理效果,便于追踪
5. **全行业受益**: 所有分类都避免表格问题

## 验证方法

观察以下日志输出:
```
[INFO] 表格空格清理: 节省 XXX 字符 (XX.X%)
[INFO] Finish reason: 1  # 1=STOP表示正常结束,不是2=MAX_TOKENS
```

如果finish_reason=1且没有大量空格清理日志,说明问题已解决。

## 测试结果

```
✓ Prompt Manager加载成功
✓ System prompt包含格式规范
✓ 包含表格约束
✓ 包含长度约束
✓ System prompt包含finance特定内容

tech: ✓ 格式规范
news: ✓ 格式规范
developer: ✓ 格式规范
```

所有行业成功继承格式规范!

## 备注

- max_output_tokens已经是65536(Gemini 2.5 Flash的最大值),无法进一步提高
- 这是Gemini API的已知bug,需要通过提示词工程和后处理来规避
- 如果问题仍然存在,可以考虑进一步减少输入文章数量或使用分段分析
- **建议**: 未来新增行业模板时,无需添加格式约束,会自动继承base.yaml
