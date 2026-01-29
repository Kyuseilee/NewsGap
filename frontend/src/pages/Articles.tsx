import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { ExternalLink, Calendar, Tag } from 'lucide-react'
import { api } from '@/services/api'
import { format } from 'date-fns'
import type { Article } from '@/types/api'

export default function ArticlesPage() {
  const [industry, setIndustry] = useState<string | undefined>()
  const [limit] = useState(50)

  const { data, isLoading } = useQuery({
    queryKey: ['articles', industry, limit],
    queryFn: () => api.getArticles({ industry, limit }),
  })

  if (isLoading) {
    return <div className="p-8 text-center">加载中...</div>
  }

  return (
    <div className="p-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">文章列表</h1>

        <div className="flex gap-4">
          <select
            value={industry || ''}
            onChange={(e) => setIndustry(e.target.value || undefined)}
            className="px-4 py-2 border border-gray-300 rounded-lg"
          >
            <option value="">全部行业</option>
            <option value="ai">AI</option>
            <option value="tech">科技</option>
            <option value="finance">金融</option>
            <option value="healthcare">医疗</option>
          </select>
        </div>
      </div>

      <div className="space-y-4">
        {data?.articles?.map((article: Article) => (
          <ArticleCard key={article.id} article={article} />
        ))}

        {data?.articles?.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            暂无文章，请先进行爬取
          </div>
        )}
      </div>
    </div>
  )
}

function ArticleCard({ article }: { article: Article }) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            {article.title}
          </h3>

          {article.summary && (
            <p className="text-gray-600 text-sm mb-3 line-clamp-2">
              {article.summary}
            </p>
          )}

          <div className="flex items-center gap-4 text-sm text-gray-500">
            <span className="flex items-center gap-1">
              <Calendar size={14} />
              {format(new Date(article.published_at), 'yyyy-MM-dd HH:mm')}
            </span>
            <span>{article.source_name}</span>
            <span className="px-2 py-1 bg-gray-100 rounded">
              {article.industry}
            </span>
          </div>

          {article.tags.length > 0 && (
            <div className="flex items-center gap-2 mt-2">
              <Tag size={14} className="text-gray-400" />
              {article.tags.map((tag) => (
                <span
                  key={tag}
                  className="text-xs px-2 py-1 bg-blue-50 text-blue-600 rounded"
                >
                  {tag}
                </span>
              ))}
            </div>
          )}
        </div>

        <a
          href={article.url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex-shrink-0 p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
        >
          <ExternalLink size={20} />
        </a>
      </div>
    </div>
  )
}
