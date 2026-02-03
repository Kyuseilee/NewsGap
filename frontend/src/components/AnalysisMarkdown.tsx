import ReactMarkdown from 'react-markdown'
import { ExternalLink } from 'lucide-react'
import { useState, useMemo } from 'react'
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
 * 支持格式：[1]、[2] 等（单方括号，匹配AI输出格式）
 * 注意：需要排除Markdown链接格式 [文字](url)
 */
export default function AnalysisMarkdown({ content, articles }: AnalysisMarkdownProps) {
  const [hoveredRef, setHoveredRef] = useState<number | null>(null)

  // 使用 useMemo 缓存引用映射，避免每次渲染都重新计算
  const refMap = useMemo(() => {
    const map = new Map<number, Article>()
    
    // 正则匹配 [数字] 格式，但排除后面跟着 ( 的情况（Markdown链接）
    const refPattern = /\[(\d+)\](?!\()/g
    let match
    const usedIndices = new Set<number>()
    
    while ((match = refPattern.exec(content)) !== null) {
      const index = parseInt(match[1], 10)
      if (!usedIndices.has(index) && index > 0 && index <= articles.length) {
        map.set(index, articles[index - 1])  // 转换为0-based索引
        usedIndices.add(index)
      }
    }
    
    return map
  }, [content, articles])

  // 自定义渲染器：将 [1] 替换为可点击的链接
  const processContent = (children: ReactNode): ReactNode => {
    const text = extractTextFromChildren(children)
    
    if (!text || typeof text !== 'string') {
      return children
    }
    
    const parts: ReactNode[] = []
    // 匹配 [数字] 但排除 Markdown 链接格式
    const refPattern = /\[(\d+)\](?!\()/g
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
            className="inline-flex items-center gap-1 px-2 py-0.5 bg-blue-50 text-blue-700 hover:bg-blue-100 rounded border border-blue-200 transition-colors text-sm font-medium no-underline"
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
        parts.push(`[${index}]`)
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
    </div>
  )
}
