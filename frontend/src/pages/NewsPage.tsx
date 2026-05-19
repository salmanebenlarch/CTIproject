import { useState } from 'react'

import { ErrorBanner } from '../components/ErrorBanner'
import { LoadingSpinner } from '../components/LoadingSpinner'
import { getNewsImageUrl } from '../lib/api'
import type { NewsCategory, NewsStory } from '../types/news'

interface NewsPageProps {
  stories: NewsStory[]
  category: NewsCategory
  loading: boolean
  error: string | null
  onRefresh: () => Promise<void>
  onCategoryChange: (category: NewsCategory) => void
}

const categoryOptions: { value: NewsCategory; label: string }[] = [
  { value: 'all', label: 'All' },
  { value: 'security', label: 'Security' },
  { value: 'ai', label: 'AI' },
  { value: 'cloud', label: 'Cloud' },
  { value: 'privacy', label: 'Privacy' },
  { value: 'devtools', label: 'Devtools' },
  { value: 'startups', label: 'Startups' },
]

function NewsThumbnail({ story }: { story: NewsStory }) {
  const [failed, setFailed] = useState(false)

  if (failed || !story.url) {
    return (
      <div className="news-thumb-placeholder">
        <span>No preview image</span>
      </div>
    )
  }

  return (
    <img
      className="news-thumb"
      src={getNewsImageUrl(story.id)}
      alt={story.title}
      loading="lazy"
      onError={() => setFailed(true)}
    />
  )
}

export function NewsPage({
  stories,
  category,
  loading,
  error,
  onRefresh,
  onCategoryChange,
}: NewsPageProps) {
  return (
    <>
      <section className="hero">
        <p className="eyebrow">Analyst awareness</p>
        <h1>Latest Hacker News stories</h1>
        <p className="hero-copy">
          Filter the feed by topic and keep the page open to auto-refresh every 5 minutes.
        </p>
        <div className="toolbar-row">
          <div className="chip-row">
            {categoryOptions.map((option) => (
              <button
                key={option.value}
                type="button"
                className={category === option.value ? 'quick-link-card active-chip' : 'quick-link-card'}
                onClick={() => onCategoryChange(option.value)}
              >
                <strong>{option.label}</strong>
              </button>
            ))}
          </div>
          <button type="button" onClick={() => void onRefresh()}>
            Refresh news
          </button>
        </div>
      </section>

      {error && <ErrorBanner message={error} />}
      {loading && <LoadingSpinner label="Loading news feed..." />}

      {!loading && !stories.length && (
        <div className="empty-state">No news items matched this category right now.</div>
      )}

      <section className="news-grid">
        {stories.map((story) => (
          <article className="card news-card" key={story.id}>
            <NewsThumbnail story={story} />
            <div className="section-header">
              <span className="counter-pill">{story.score} points</span>
              <span className="muted-copy">{story.descendants} comments</span>
            </div>
            <h3>{story.title}</h3>
            <p className="muted-copy">
              by {story.by ?? 'unknown'} • {new Date(story.time * 1000).toLocaleString()}
            </p>
            <div className="chip-row news-tags">
              {(story.categories.length ? story.categories : ['all']).map((tag) => (
                <span className="data-chip muted" key={`${story.id}-${tag}`}>
                  {tag}
                </span>
              ))}
            </div>
            <div className="news-links">
              <a href={story.url ?? story.hn_url} target="_blank" rel="noreferrer">
                Open story
              </a>
              <a href={story.hn_url} target="_blank" rel="noreferrer">
                Discussion
              </a>
            </div>
          </article>
        ))}
      </section>
    </>
  )
}
