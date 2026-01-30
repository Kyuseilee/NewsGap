import ReactMarkdown from 'react-markdown'
import { ExternalLink } from 'lucide-react'
import { useState } from 'react'
import type { Article } from '@/types/api'
import type { ReactNode } from 'react'

interface AnalysisMarkdownProps {
  content: string
  articles: Article[]
}

/**
 * 递归提取React children中的文本内容
 */
function extractTextFromChildren(children: ReactNode): string {
  if (typeof children === 'string') {
    return children
  }
  if (typeof children === 'number') {
    return String(children)
  }
  if (Array.isArray(children)) {
    return children.map(extractTextFromChildren).join('')
  }
  if (children && typeof children === 'object' && 'props' in children) {
    return extractTextFromChildren(children.props.children)
  }
  return ''
}

/**
 * 解析Markdown中的文章引用并渲染为可点击链接
 * 支持格式：[[1]]、[[2]] 等
 */
export default function AnalysisMarkdown({ content, articles }: AnalysisMarkdownProps) {
  const [hoveredRef, setHoveredRef] = useState<number | null>(null)

  // 从Markdown中提取引用索引到文章的映射
  // 查找类似 "[[1]] 文章标题" 的模式
  const parseArticleReferences = (): Map<number, Article> => {
    const refMap = new Map<number, Article>()
    
    // 正则匹配 [[数字]] 格式
    const refPattern = /\[\[(\d+)\]\]/g
    let match
    const usedIndices = new Set<number>()
    
    while ((match = refPattern.exec(content)) !== null) {
      const index = parseInt(match[1], 10)
      if (!usedIndices.has(index) && index > 0 && index <= articles.length) {
        refMap.set(index, articles[index - 1])  // 转换为0-based索引
        usedIndices.add(index)
      }
    }
    
    return refMap
  }

  const refMap = parseArticleReferences()

  // 自定义渲染器：将 [[1]] 替换为可点击的链接
  const processContent = (children: ReactNode): ReactNode => {
    const text = extractTextFromChildren(children)
    
    if (!text || typeof text !== 'string') {
      return children
    }
    
    const parts: ReactNode[] = []
    const refPattern = /\[\[(\d+)\]\]/g
    let lastIndex = 0
    let match

    while ((match = refPattern.exec(text)) !== null) {
      const index = parseInt(match[1], 10)
      const article = refMap.get(index)

      // 添加引用之前的文本
      if (match.index > lastIndex) {
        parts.push(text.substring(lastIndex, match.index))
      }

      // 添加引用链接
      if (article) {
        parts.push(
          <a
            key={`ref-${match.index}-${index}`}
            href={article.url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 px-2 py-0.5 bg-blue-50 text-blue-700 hover:bg-blue-100 rounded border border-blue-200 transition-colors text-sm font-medium"
            onMouseEnter={() => setHoveredRef(index)}
            onMouseLeave={() => setHoveredRef(null)}
            title={`${article.title}\n来源：${article.source_name}\n点击查看原文`}
          >
            <span>[{index}]</span>
            {hoveredRef === index && (
              <ExternalLink size={12} />
            )}
          </a>
        )
      } else {
        // 如果找不到对应的文章，保持原样
        parts.push(`[[${index}]]`)
      }

      lastIndex = match.index + match[0].length
    }

    // 添加剩余文本
    if (lastIndex < text.length) {
      parts.push(text.substring(lastIndex))
    }

    return parts.length > 0 ? parts : children
  }

  return (
    <div className="prose prose-lg max-w-none">
      <ReactMarkdown
        components={{
          // 自定义段落渲染，处理文章引用
          p: ({ children }) => {
            return <p>{processContent(children)}</p>
          },
          // 自定义列表项渲染
          li: ({ children }) => {
            return <li>{processContent(children)}</li>
          },
          // 自定义标题渲染
          h1: ({ children }) => <h1 className="text-3xl font-bold mt-8 mb-4">{children}</h1>,
          h2: ({ children }) => <h2 className="text-2xl font-bold mt-6 mb-3">{children}</h2>,
          h3: ({ children }) => <h3 className="text-xl font-semibold mt-4 mb-2">{children}</h3>,
          
          // 自定义链接样式
          a: ({ href, children }) => (
            <a
              href={href}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-800 underline"
            >
              {children}
            </a>
          ),
          
          // 自定义代码块样式
          code: ({ className, children, ...props }) => {
            const isInline = !className
            if (isInline) {
              return (
                <code className="px-1.5 py-0.5 bg-gray-100 text-gray-800 rounded text-sm font-mono" {...props}>
                  {children}
                </code>
              )
            }
            return (
              <code className="block p-4 bg-gray-50 rounded-lg text-sm font-mono overflow-x-auto" {...props}>
                {children}
              </code>
            )
          },
          
          // 自定义引用块样式
          blockquote: ({ children }) => (
            <blockquote className="border-l-4 border-blue-500 pl-4 italic text-gray-700 my-4">
              {children}
            </blockquote>
          ),
        }}
      >
        {content}
      </ReactMarkdown>

      {/* 文章引用索引表（如果存在引用） */}
      {refMap.size > 0 && (
        <div className="mt-8 pt-6 border-t border-gray-200">
          <h3 className="text-lg font-semibold mb-4">📚 引用文章</h3>
          <div className="space-y-2">
            {Array.from(refMap.entries())
              .sort((a, b) => a[0] - b[0])
              .map(([index, article]) => (
                <div
                  key={article.id}
                  className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <span className="flex-shrink-0 w-8 h-8 flex items-center justify-center bg-blue-100 text-blue-700 rounded font-semibold text-sm">
                    {index}
                  </span>
                  <div className="flex-1 min-w-0">
                    <a
                      href={article.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-800 hover:underline font-medium block truncate"
                    >
                      {article.title}
                    </a>
                    <div className="text-sm text-gray-500 mt-1">
                      来源：{article.source_name} · {new Date(article.published_at).toLocaleString('zh-CN')}
                    </div>
                  </div>
                  <a
                    href={article.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex-shrink-0 text-gray-400 hover:text-blue-600 transition-colors"
                  >
                    <ExternalLink size={18} />
                  </a>
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  )
}
