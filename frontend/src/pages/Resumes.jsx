import { useEffect, useState } from 'react';
import api from '../api';
import { Link } from 'react-router-dom';

export default function Resumes() {
  const [data, setData] = useState(null);
  const [error, setError] = useState('');
  const [search, setSearch] = useState('');
  const [minimumScore, setMinimumScore] = useState('');
  const [page, setPage] = useState(1);
  async function loadCandidates() {
    setError('');
    try {
      const response = await api.get('/resumes', { params: { search, min_score: minimumScore || undefined, page, page_size: 15 } });
      const result = response.data || {};
      setData({ items: Array.isArray(result.items) ? result.items : [], total: Number(result.total) || 0, page: result.page || page, page_size: result.page_size || 15 });
    } catch (requestError) {
      setData(null);
      setError(requestError.response?.data?.detail || requestError.message || 'Unable to load candidates.');
    }
  }
  useEffect(() => { loadCandidates(); }, [search, minimumScore, page]);
  async function removeCandidate(id) {
    if (!window.confirm('Delete this resume?')) return;
    try { await api.delete(`/resumes/${id}`); loadCandidates(); }
    catch (requestError) { setError(requestError.response?.data?.detail || 'Unable to delete resume.'); }
  }
  return <section className="card"><div className="section-title"><div><h2>Candidate ranking</h2><p>Sorted by score descending in the database.</p></div><div className="filters"><input placeholder="Search name or email" value={search} onChange={(event) => { setPage(1); setSearch(event.target.value); }} /><select value={minimumScore} onChange={(event) => { setPage(1); setMinimumScore(event.target.value); }}><option value="">All scores</option><option value="80">80 and above</option><option value="60">60 and above</option></select></div></div>{error && <p className="error">{error}</p>}{!data && !error && <p>Loading candidates...</p>}{data && <>{data.items.length === 0 ? <p className="muted">No candidates match the current filters.</p> : <div className="table-wrap"><table><thead><tr><th>Rank</th><th>Candidate</th><th>Filename</th><th>Email</th><th>Extracted skills</th><th>Skills</th><th>ATS</th><th>Overall</th><th>Actions</th></tr></thead><tbody>{data.items.map((resume) => <tr key={resume.id}><td>#{resume.rank}</td><td>{resume.candidate_name}</td><td>{resume.filename}</td><td>{resume.email || '—'}</td><td>{resume.skills?.join(', ') || 'No matched skills'}</td><td>{resume.skills_score}/30</td><td>{resume.ats_score}/15</td><td><b className="score">{resume.overall_score}/100</b></td><td><Link to={`/resume/${resume.id}`}>View</Link>{' '}<button className="link danger" onClick={() => removeCandidate(resume.id)}>Delete</button></td></tr>)}</tbody></table></div>}<div className="pager"><span>{data.total} results</span><button disabled={page === 1} onClick={() => setPage(page - 1)}>Previous</button><span>Page {page}</span><button disabled={page * data.page_size >= data.total} onClick={() => setPage(page + 1)}>Next</button></div></>}</section>;
}
