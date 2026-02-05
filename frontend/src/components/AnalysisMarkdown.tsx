import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import rehypeRaw from 'rehype-raw'
import { ExternalLink } from 'lucide-react'
import { useState, useMemo, useEffect, useRef } from 'react'
import mermaid from 'mermaid'
import type { Article } from '@/types/api'
import type { ReactNode } from 'react'

interface AnalysisMarkdownProps {
  content: string
  articles: Article[]
}

// 初始化Mermaid
mermaid.initialize({
  startOnLoad: false,
  theme: 'default',
  securityLevel: 'loose',
  fontFamily: 'ui-sans-serif, system-ui, sans-serif',
})

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
 * Mermaid流程图组件
 */
function MermaidDiagram({ chart }: { chart: string }) {
  const ref = useRef<HTMLDivElement>(null)
  const [svg, setSvg] = useState<string>('')
  const [error, setError] = useState<string>('')

  useEffect(() => {
    const renderDiagram = async () => {
      if (!ref.current) return
      
      try {
        // 生成唯一ID
        const id = `mermaid-${Math.random().toString(36).substr(2, 9)}`
        
        // 渲染Mermaid图表
        const { svg } = await mermaid.render(id, chart)
        setSvg(svg)
        setError('')
      } catch (err) {
        console.error('Mermaid rendering error:', err)
        setError(err instanceof Error ? err.message : 'Failed to render diagram')
      }
    }

    renderDiagram()
  }, [chart])

  if (error) {
    return (
      <div className="border border-red-300 bg-red-50 p-4 rounded-lg my-4">
        <p className="text-red-700 text-sm font-medium">流程图渲染失败</p>
        <pre className="text-xs text-red-600 mt-2 overflow-x-auto">{error}</pre>
      </div>
    )
  }

  return (
    <div 
      ref={ref} 
      className="mermaid-diagram my-6 flex justify-center items-center bg-white p-4 rounded-lg border border-gray-200"
      dangerouslySetInnerHTML={{ __html: svg }}
    />
  )
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
        remarkPlugins={[remarkGfm]}
        rehypePlugins={[rehypeRaw]}
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
          h4: ({ children }) => <h4 className="text-lg font-semibold mt-3 mb-2">{children}</h4>,
          
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
          
          // 自定义代码块样式，支持Mermaid流程图
          code: ({ className, children, ...props }) => {
            const match = /language-(\w+)/.exec(className || '')
            const language = match ? match[1] : ''
            const isInline = !className
            const code = String(children).replace(/\n$/, '')

            // 如果是Mermaid图表
            if (language === 'mermaid') {
              return <MermaidDiagram chart={code} />
            }

            // 行内代码
            if (isInline) {
              return (
                <code className="px-1.5 py-0.5 bg-gray-100 text-gray-800 rounded text-sm font-mono" {...props}>
                  {children}
                </code>
              )
            }

            // 代码块
            return (
              <div className="my-4">
                {language && (
                  <div className="bg-gray-700 text-gray-300 px-4 py-2 rounded-t-lg text-xs font-medium">
                    {language}
                  </div>
                )}
                <pre className={`${language ? 'rounded-t-none' : 'rounded-lg'} bg-gray-50 border border-gray-200 overflow-x-auto`}>
                  <code className="block p-4 text-sm font-mono text-gray-800" {...props}>
                    {children}
                  </code>
                </pre>
              </div>
            )
          },
          
          // 自定义引用块样式
          blockquote: ({ children }) => (
            <blockquote className="border-l-4 border-blue-500 pl-4 italic text-gray-700 my-4 bg-blue-50 py-2">
              {children}
            </blockquote>
          ),

          // 表格支持（GFM）
          table: ({ children }) => (
            <div className="overflow-x-auto my-6">
              <table className="min-w-full divide-y divide-gray-300 border border-gray-300">
                {children}
              </table>
            </div>
          ),
          thead: ({ children }) => (
            <thead className="bg-gray-50">{children}</thead>
          ),
          tbody: ({ children }) => (
            <tbody className="divide-y divide-gray-200 bg-white">{children}</tbody>
          ),
          tr: ({ children }) => (
            <tr>{children}</tr>
          ),
          th: ({ children }) => (
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider border-r border-gray-300 last:border-r-0">
              {children}
            </th>
          ),
          td: ({ children }) => (
            <td className="px-4 py-3 text-sm text-gray-900 border-r border-gray-200 last:border-r-0">
              {children}
            </td>
          ),

          // 任务列表支持（GFM）
          input: ({ type, checked, disabled }) => {
            if (type === 'checkbox') {
              return (
                <input
                  type="checkbox"
                  checked={checked}
                  disabled={disabled}
                  readOnly
                  className="mr-2 h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
              )
            }
            return <input type={type} />
          },

          // 分割线
          hr: () => <hr className="my-8 border-gray-300" />,

          // 删除线（GFM）
          del: ({ children }) => (
            <del className="text-gray-500">{children}</del>
          ),
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  )
}
