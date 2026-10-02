import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Bar, BarChart, CartesianGrid, Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import api from '../api';

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    api.get('/dashboard')
      .then((response) => setData(response.data))
      .catch((requestError) => setError(requestError.response?.data?.detail || requestError.message || 'Unable to load dashboard.'));
  }, []);

  if (error) return <section className="card"><p className="error">{error}</p></section>;
  if (!data) return <section className="card loading">Loading dashboard...</section>;

  return <>
    <section className="metrics">
      <div className="card metric"><span>Total resumes</span><strong>{data.total_resumes}</strong></div>
      <div className="card metric"><span>Average score</span><strong>{data.average_score}</strong></div>
      <div className="card metric"><span>Highest score</span><strong>{data.highest_score}</strong></div>
      <div className="card metric"><span>Lowest score</span><strong>{data.lowest_score}</strong></div>
    </section>
    <section className="charts">
      <div className="card"><div className="section-title"><div><h2>Score distribution</h2><p>Candidate scores across the database.</p></div></div><ResponsiveContainer width="100%" height={260}><BarChart data={data.score_distribution}><CartesianGrid strokeDasharray="3 3" vertical={false} /><XAxis dataKey="range" /><YAxis allowDecimals={false} /><Tooltip /><Bar dataKey="count" fill="#6d5dfc" radius={[4, 4, 0, 0]} /></BarChart></ResponsiveContainer></div>
      <div className="card"><div className="section-title"><div><h2>Candidate score pie chart</h2><p>Complete colored score circle by candidate.</p></div></div>{data.candidate_scores.length === 0 ? <p className="muted">No candidates yet.</p> : <ResponsiveContainer width="100%" height={300}><PieChart><Pie data={data.candidate_scores} dataKey="score" nameKey="name" cx="50%" cy="43%" innerRadius={0} outerRadius={102} startAngle={90} endAngle={-270} paddingAngle={2} label={({ score }) => score} labelLine={false}>{data.candidate_scores.map((candidate, index) => <Cell key={`${candidate.name}-${index}`} fill={['#6d5dfc', '#168866', '#e07a3f', '#d54359', '#3c8dbc'][index % 5]} />)}</Pie><Tooltip formatter={(value, name) => [`${value}/100`, name]} /><Legend verticalAlign="bottom" height={42} /></PieChart></ResponsiveContainer>}</div>
      <div className="card"><div className="section-title"><div><h2>Category averages</h2><p>Performance across evaluated resumes.</p></div></div>{data.category_scores.map((category) => <div className="break" key={category.category}><span>{category.category}</span><b>{category.score}/{category.maximum}</b><i><em style={{ width: `${category.maximum ? (category.score / category.maximum) * 100 : 0}%` }} /></i></div>)}</div>
      <div className="card"><div className="section-title"><div><h2>Skill distribution</h2><p>Most frequently extracted skills.</p></div></div>{data.skill_distribution.length === 0 ? <p className="muted">No skills extracted yet.</p> : <ResponsiveContainer width="100%" height={260}><BarChart data={data.skill_distribution} layout="vertical" margin={{ left: 18, right: 12 }}><CartesianGrid strokeDasharray="3 3" horizontal={false} /><XAxis type="number" allowDecimals={false} /><YAxis type="category" dataKey="skill" width={85} tick={{ fontSize: 11 }} /><Tooltip /><Bar dataKey="count" fill="#e07a3f" radius={[0, 4, 4, 0]} /></BarChart></ResponsiveContainer>}</div>
    </section>
    <section className="card"><div className="section-title"><div><h2>Recent uploads</h2><p>Latest resumes in the ranking.</p></div><Link className="button" to="/resumes">View candidates</Link></div>{data.recent_uploads.length === 0 ? <p className="muted">Upload a resume to populate the dashboard.</p> : <div className="table-wrap"><table><thead><tr><th>Rank</th><th>Candidate</th><th>Filename</th><th>Score</th><th /></tr></thead><tbody>{data.recent_uploads.map((resume) => <tr key={resume.id}><td>#{resume.rank}</td><td>{resume.candidate_name}</td><td>{resume.filename}</td><td><b className="score">{resume.overall_score}/100</b></td><td><Link to={`/resume/${resume.id}`}>View</Link></td></tr>)}</tbody></table></div>}</section>
  </>;
}