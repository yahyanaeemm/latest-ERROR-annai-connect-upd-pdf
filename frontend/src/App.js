import React, { useState, useEffect, useRef } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import axios from "axios";
import { Button } from "./components/ui/button";
import { Input } from "./components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";
import { Badge } from "./components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./components/ui/table";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "./components/ui/dialog";
import { Label } from "./components/ui/label";
import { Textarea } from "./components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./components/ui/select";
import { 
  Upload, Users, GraduationCap, DollarSign, FileText, Eye, CheckCircle, XCircle, Clock, Pen, Plus, Edit, 
  Trash2, Download, Archive, Settings, Trophy, Medal, Crown, TrendingUp, Calendar, Filter,
  Star, Award, Target, BarChart3, Activity, Zap
} from "lucide-react";
import SignatureCanvas from 'react-signature-canvas';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Auth Context (REMOVED THEME CONTEXT)
const AuthContext = React.createContext();

const useAuth = () => {
  const context = React.useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      fetchCurrentUser();
    } else {
      setLoading(false);
    }
  }, []);

  const fetchCurrentUser = async () => {
    try {
      const response = await axios.get(`${API}/me`);
      setUser(response.data);
    } catch (error) {
      localStorage.removeItem('token');
      delete axios.defaults.headers.common['Authorization'];
    } finally {
      setLoading(false);
    }
  };

  const login = async (username, password) => {
    try {
      const response = await axios.post(`${API}/login`, { username, password });
      const { access_token, role, user_id } = response.data;
      
      localStorage.setItem('token', access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      await fetchCurrentUser();
      return true;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Login failed');
    }
  };

  const register = async (userData) => {
    try {
      const response = await axios.post(`${API}/register`, userData);
      return response.data; // Return the whole response with message and status
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Registration failed');
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

// Components
const LoginForm = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    email: '',
    role: 'agent',
    agent_id: ''
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const { login, register } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      if (isLogin) {
        await login(formData.username, formData.password);
      } else {
        const result = await register(formData);
        if (result.status === 'pending') {
          setSuccess(result.message);
          setFormData({
            username: '',
            password: '',
            email: '',
            role: 'agent',
            agent_id: ''
          });
        }
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-800 flex items-center justify-center p-4">
      <Card className="w-full max-w-md bg-white/95 backdrop-blur-sm shadow-2xl border-0">
        <CardHeader className="text-center pb-2">
          <CardTitle className="text-2xl font-bold text-slate-800">
            {isLogin ? 'Login' : 'Register'}
          </CardTitle>
          <CardDescription className="text-slate-600">
            Educational Institution Admission System
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="username">Username</Label>
              <Input
                id="username"
                type="text"
                value={formData.username}
                onChange={(e) => setFormData({...formData, username: e.target.value})}
                required
                className="mt-1"
              />
            </div>

            {!isLogin && (
              <div>
                <Label htmlFor="email">Email</Label>
                <Input
                  id="email"
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  required
                  className="mt-1"
                />
              </div>
            )}

            <div>
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({...formData, password: e.target.value})}
                required
                className="mt-1"
              />
            </div>

            {!isLogin && (
              <>
                <div>
                  <Label htmlFor="role">Role</Label>
                  <Select value={formData.role} onValueChange={(value) => setFormData({...formData, role: value})}>
                    <SelectTrigger className="mt-1">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="agent">Agent</SelectItem>
                      <SelectItem value="coordinator">Admission Coordinator</SelectItem>
                      <SelectItem value="admin">Admin</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {formData.role === 'agent' && (
                  <div>
                    <Label htmlFor="agent_id">Agent ID</Label>
                    <Input
                      id="agent_id"
                      type="text"
                      value={formData.agent_id}
                      onChange={(e) => setFormData({...formData, agent_id: e.target.value})}
                      placeholder="Optional: Custom Agent ID"
                      className="mt-1"
                    />
                  </div>
                )}
              </>
            )}

            {error && (
              <div className="text-red-600 text-sm text-center">{error}</div>
            )}

            {success && (
              <div className="text-green-600 text-sm text-center bg-green-50 p-3 rounded border border-green-200">
                {success}
              </div>
            )}

            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? 'Please wait...' : (isLogin ? 'Login' : 'Register')}
            </Button>
          </form>

          <div className="text-center">
            <button
              type="button"
              onClick={() => setIsLogin(!isLogin)}
              className="text-blue-600 hover:text-blue-800 text-sm underline"
            >
              {isLogin ? 'Need an account? Register' : 'Have an account? Login'}
            </button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

const Header = () => {
  const { user, logout } = useAuth();

  return (
    <header className="bg-gradient-to-r from-slate-900 via-blue-900 to-slate-900 text-white p-4 shadow-2xl border-b border-blue-800/30">
      <div className="container mx-auto flex justify-between items-center">
        <div className="flex items-center space-x-3">
          <div className="relative">
            <GraduationCap className="h-10 w-10 text-yellow-400 drop-shadow-lg" />
            <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-400 rounded-full animate-pulse"></div>
          </div>
          <div>
            <h1 className="text-2xl font-bold bg-gradient-to-r from-yellow-400 to-yellow-300 bg-clip-text text-transparent">
              EduAdmit Pro
            </h1>
            <p className="text-xs text-slate-300 hidden sm:block">Student Admission Management</p>
          </div>
        </div>
        
        <div className="flex items-center space-x-4">
          {/* User Info */}
          <div className="flex items-center space-x-3">
            <Badge variant="outline" className="bg-gradient-to-r from-yellow-400 to-yellow-500 text-slate-900 border-yellow-400 font-semibold px-3 py-1 shadow-lg">
              {user?.role?.toUpperCase()}
            </Badge>
            <div className="hidden sm:block text-right">
              <div className="text-sm font-medium">Welcome back!</div>
              <div className="text-xs text-slate-300">{user?.username}</div>
            </div>
          </div>
          
          <Button 
            variant="outline" 
            size="sm" 
            onClick={logout}
            className="border-red-400 text-red-400 hover:bg-red-400 hover:text-white transition-all duration-300 shadow-lg"
          >
            Logout
          </Button>
        </div>
      </div>
    </header>
  );
};

// Simple Working Leaderboard Component
const SimpleLeaderboard = () => {
  const [leaderboardData, setLeaderboardData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('overall');

  const fetchLeaderboard = async (type = 'overall') => {
    setLoading(true);
    try {
      const response = await axios.get(`${API}/leaderboard/${type}`);
      setLeaderboardData(response.data);
    } catch (error) {
      console.error('Error fetching leaderboard:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLeaderboard(activeTab);
  }, [activeTab]);

  return (
    <div className="space-y-6">
      <Card className="shadow-lg">
        <CardHeader>
          <div className="flex items-center space-x-3">
            <Trophy className="h-8 w-8 text-yellow-500" />
            <div>
              <CardTitle className="text-2xl font-bold text-blue-600">Agent Leaderboard</CardTitle>
              <CardDescription>Performance rankings and achievements</CardDescription>
            </div>
          </div>
        </CardHeader>
        
        <CardContent>
          <Tabs value={activeTab} onValueChange={setActiveTab}>
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="overall">Overall</TabsTrigger>
              <TabsTrigger value="weekly">Weekly</TabsTrigger>
              <TabsTrigger value="monthly">Monthly</TabsTrigger>
            </TabsList>
            
            <div className="mt-6">
              {loading ? (
                <div className="flex justify-center py-12">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                </div>
              ) : leaderboardData?.leaderboard?.length > 0 ? (
                <>
                  {/* Top 3 Agents */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                    {leaderboardData.leaderboard.slice(0, 3).map((agent, index) => (
                      <Card key={agent.agent_id} className={`text-center ${
                        index === 0 ? 'ring-2 ring-yellow-400 bg-yellow-50' : 
                        index === 1 ? 'ring-2 ring-gray-400 bg-gray-50' : 
                        'ring-2 ring-amber-600 bg-amber-50'
                      }`}>
                        <CardHeader>
                          <div className="flex justify-center mb-2">
                            {index === 0 ? <Crown className="h-8 w-8 text-yellow-500" /> :
                             index === 1 ? <Medal className="h-8 w-8 text-gray-500" /> :
                             <Award className="h-8 w-8 text-amber-600" />}
                          </div>
                          <CardTitle className="text-lg">{agent.full_name}</CardTitle>
                          <Badge className={
                            index === 0 ? 'bg-yellow-500 text-white' :
                            index === 1 ? 'bg-gray-500 text-white' :
                            'bg-amber-600 text-white'
                          }>
                            #{agent.rank} Place
                          </Badge>
                        </CardHeader>
                        <CardContent>
                          <div className="space-y-2">
                            <div className="text-2xl font-bold text-blue-600">
                              {activeTab === 'overall' ? agent.total_admissions : agent.period_admissions}
                            </div>
                            <div className="text-sm text-gray-600">Students</div>
                            <div className="text-lg font-semibold text-green-600">
                              ₹{(activeTab === 'overall' ? agent.total_incentive : agent.period_incentive || 0).toLocaleString('en-IN')}
                            </div>
                            <div className="text-xs text-gray-500">Incentives</div>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>

                  {/* Complete Rankings */}
                  <Card>
                    <CardHeader>
                      <CardTitle>Complete Rankings</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>Rank</TableHead>
                            <TableHead>Agent</TableHead>
                            <TableHead>Students</TableHead>
                            <TableHead>Incentives</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {leaderboardData.leaderboard.slice(0, 10).map((agent, index) => (
                            <TableRow key={agent.agent_id} className={`
                              ${index < 3 ? 'bg-gradient-to-r hover:shadow-lg transition-all duration-300' : ''}
                              ${index === 0 ? 'from-yellow-50 to-yellow-100 border-l-4 border-yellow-400' : ''}
                              ${index === 1 ? 'from-gray-50 to-gray-100 border-l-4 border-gray-400' : ''}
                              ${index === 2 ? 'from-amber-50 to-amber-100 border-l-4 border-amber-600' : ''}
                              ${index >= 3 ? 'hover:bg-slate-50' : ''}
                            `}>
                              <TableCell>
                                <Badge variant="outline" className={`
                                  ${index === 0 ? 'bg-yellow-500 text-white border-yellow-500' : ''}
                                  ${index === 1 ? 'bg-gray-500 text-white border-gray-500' : ''}
                                  ${index === 2 ? 'bg-amber-600 text-white border-amber-600' : ''}
                                `}>
                                  #{agent.rank}
                                </Badge>
                              </TableCell>
                              <TableCell>
                                <div className="flex items-center space-x-3">
                                  {index < 3 && (
                                    <div className="flex-shrink-0">
                                      {index === 0 ? <Crown className="h-5 w-5 text-yellow-500" /> :
                                       index === 1 ? <Medal className="h-5 w-5 text-gray-500" /> :
                                       <Award className="h-5 w-5 text-amber-600" />}
                                    </div>
                                  )}
                                  <div>
                                    <div className={`font-semibold ${index < 3 ? 'text-lg' : ''}`}>
                                      {agent.full_name}
                                    </div>
                                    <div className="text-sm text-gray-500">@{agent.username}</div>
                                  </div>
                                </div>
                              </TableCell>
                              <TableCell>
                                <div className={`font-bold text-blue-600 ${index < 3 ? 'text-xl' : 'text-lg'}`}>
                                  {activeTab === 'overall' ? agent.total_admissions : agent.period_admissions}
                                </div>
                              </TableCell>
                              <TableCell>
                                <div className={`font-bold text-green-600 ${index < 3 ? 'text-xl' : 'text-lg'}`}>
                                  ₹{(activeTab === 'overall' ? agent.total_incentive : agent.period_incentive || 0).toLocaleString('en-IN')}
                                </div>
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </CardContent>
                  </Card>
                </>
              ) : (
                <div className="text-center py-12">
                  <Trophy className="h-16 w-16 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500">No leaderboard data available</p>
                </div>
              )}
            </div>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
};

const AgentDashboard = () => {
  const [students, setStudents] = useState([]);
  const [incentives, setIncentives] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [courseRules, setCourseRules] = useState([]);
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    course: ''
  });

  useEffect(() => {
    fetchStudents();
    fetchIncentives();
    fetchCourseRules();
  }, []);

  const fetchStudents = async () => {
    try {
      const response = await axios.get(`${API}/students`);
      setStudents(response.data);
    } catch (error) {
      console.error('Error fetching students:', error);
    }
  };

  const fetchIncentives = async () => {
    try {
      const response = await axios.get(`${API}/incentives`);
      setIncentives(response.data);
    } catch (error) {
      console.error('Error fetching incentives:', error);
    }
  };

  const fetchCourseRules = async () => {
    try {
      const response = await axios.get(`${API}/incentive-rules`);
      setCourseRules(response.data);
    } catch (error) {
      console.error('Error fetching course rules:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/students`, formData);
      setShowForm(false);
      setFormData({ first_name: '', last_name: '', email: '', phone: '', course: '' });
      fetchStudents();
    } catch (error) {
      console.error('Error creating student:', error);
    }
  };

  const handleFileUpload = async (studentId, documentType, file) => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('document_type', documentType);

    try {
      await axios.post(`${API}/students/${studentId}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      fetchStudents();
    } catch (error) {
      console.error('Error uploading file:', error);
    }
  };

  const downloadReceipt = async (studentId, tokenNumber) => {
    try {
      const response = await axios.get(`${API}/students/${studentId}/receipt`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `receipt_${tokenNumber}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading receipt:', error);
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      pending: { color: 'bg-yellow-100 text-yellow-800 border-yellow-300', icon: Clock },
      verified: { color: 'bg-blue-100 text-blue-800 border-blue-300', icon: Eye },
      approved: { color: 'bg-green-100 text-green-800 border-green-300', icon: CheckCircle },
      rejected: { color: 'bg-red-100 text-red-800 border-red-300', icon: XCircle }
    };

    const config = statusConfig[status] || statusConfig.pending;
    const IconComponent = config.icon;

    return (
      <Badge className={`${config.color} border flex items-center gap-1`}>
        <IconComponent className="h-3 w-3" />
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    );
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-slate-800">Agent Dashboard</h2>
        <Button onClick={() => setShowForm(true)} className="bg-blue-600 hover:bg-blue-700">
          <Users className="h-4 w-4 mr-2" />
          New Student
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Submissions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{students.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Earned</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">₹{incentives?.total_earned || 0}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Pending Incentives</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">₹{incentives?.total_pending || 0}</div>
          </CardContent>
        </Card>
      </div>

      {/* Students Table */}
      <Card>
        <CardHeader>
          <CardTitle>Student Submissions</CardTitle>
          <CardDescription>Track your student submissions and their status</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Token</TableHead>
                <TableHead>Name</TableHead>
                <TableHead>Course</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Documents</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {students.map((student) => (
                <TableRow key={student.id} className={
                  student.status === 'approved' ? 'bg-green-50 border-l-4 border-green-400' :
                  student.status === 'rejected' ? 'bg-red-50 border-l-4 border-red-400' :
                  student.status === 'pending' ? 'bg-yellow-50 border-l-4 border-yellow-400' : ''
                }>
                  <TableCell className="font-mono text-sm">{student.token_number}</TableCell>
                  <TableCell>{student.first_name} {student.last_name}</TableCell>
                  <TableCell>{student.course}</TableCell>
                  <TableCell>{getStatusBadge(student.status)}</TableCell>
                  <TableCell>
                    <div className="flex space-x-1">
                      {['tc', 'id_proof', 'marksheet'].map((docType) => (
                        <label key={docType} className="cursor-pointer">
                          <input
                            type="file"
                            className="hidden"
                            accept=".jpg,.jpeg,.pdf,.png"
                            onChange={(e) => e.target.files[0] && handleFileUpload(student.id, docType, e.target.files[0])}
                          />
                          <Badge variant={student.documents[docType] ? "default" : "outline"} className="text-xs hover:bg-blue-100">
                            {docType.replace('_', ' ').toUpperCase()}
                            {!student.documents[docType] && <Upload className="h-3 w-3 ml-1" />}
                          </Badge>
                        </label>
                      ))}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex space-x-1">
                      <Button variant="outline" size="sm">
                        <Eye className="h-4 w-4" />
                      </Button>
                      {student.status === 'approved' && (
                        <Button 
                          variant="outline" 
                          size="sm"
                          onClick={() => downloadReceipt(student.id, student.token_number)}
                          title="Download Receipt (Available for approved students only)"
                        >
                          <Download className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* New Student Form Dialog */}
      <Dialog open={showForm} onOpenChange={setShowForm}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>New Student Admission</DialogTitle>
            <DialogDescription>
              Enter student details to create a new admission record
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="first_name">First Name</Label>
                <Input
                  id="first_name"
                  value={formData.first_name}
                  onChange={(e) => setFormData({...formData, first_name: e.target.value})}
                  required
                />
              </div>
              <div>
                <Label htmlFor="last_name">Last Name</Label>
                <Input
                  id="last_name"
                  value={formData.last_name}
                  onChange={(e) => setFormData({...formData, last_name: e.target.value})}
                  required
                />
              </div>
            </div>
            <div>
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
                required
              />
            </div>
            <div>
              <Label htmlFor="phone">Phone</Label>
              <Input
                id="phone"
                value={formData.phone}
                onChange={(e) => setFormData({...formData, phone: e.target.value})}
                required
              />
            </div>
            <div>
              <Label htmlFor="course">Course</Label>
              <Select value={formData.course} onValueChange={(value) => setFormData({...formData, course: value})}>
                <SelectTrigger>
                  <SelectValue placeholder="Select a course" />
                </SelectTrigger>
                <SelectContent>
                  {courseRules.map((rule) => (
                    <SelectItem key={rule.course} value={rule.course}>
                      {rule.course} (₹{rule.amount} incentive)
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="flex justify-end space-x-2">
              <Button type="button" variant="outline" onClick={() => setShowForm(false)}>
                Cancel
              </Button>
              <Button type="submit">Create Student</Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};

// Signature Component
const SignatureModal = ({ isOpen, onClose, onSave }) => {
  const sigCanvas = useRef({});
  const [signatureType, setSignatureType] = useState('draw');
  const [uploadedImage, setUploadedImage] = useState(null);

  const clearSignature = () => {
    sigCanvas.current.clear();
  };

  const saveSignature = () => {
    let signatureData = '';
    if (signatureType === 'draw') {
      if (sigCanvas.current.isEmpty()) {
        alert('Please provide a signature');
        return;
      }
      signatureData = sigCanvas.current.toDataURL();
    } else {
      if (!uploadedImage) {
        alert('Please upload a signature image');
        return;
      }
      signatureData = uploadedImage;
    }
    
    onSave(signatureData, signatureType);
    onClose();
  };

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (!file.type.match(/image\/(png|jpg|jpeg)/)) {
        alert('Please upload a PNG or JPG image');
        return;
      }
      const reader = new FileReader();
      reader.onload = (event) => {
        setUploadedImage(event.target.result);
      };
      reader.readAsDataURL(file);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Add E-Signature</DialogTitle>
          <DialogDescription>
            Draw your signature or upload an image
          </DialogDescription>
        </DialogHeader>
        
        <Tabs value={signatureType} onValueChange={setSignatureType}>
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="draw">Draw</TabsTrigger>
            <TabsTrigger value="upload">Upload</TabsTrigger>
          </TabsList>
          
          <TabsContent value="draw" className="space-y-4">
            <div className="border rounded-lg bg-white">
              <SignatureCanvas
                ref={sigCanvas}
                canvasProps={{
                  width: 400,
                  height: 200,
                  className: 'sigCanvas'
                }}
              />
            </div>
            <Button variant="outline" onClick={clearSignature} className="w-full">
              Clear
            </Button>
          </TabsContent>
          
          <TabsContent value="upload" className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="signature-upload">Upload Signature Image</Label>
              <Input
                id="signature-upload"
                type="file"
                accept=".png,.jpg,.jpeg"
                onChange={handleImageUpload}
              />
            </div>
            {uploadedImage && (
              <div className="border rounded p-4">
                <img src={uploadedImage} alt="Uploaded signature" className="max-h-32 mx-auto" />
              </div>
            )}
          </TabsContent>
        </Tabs>
        
        <div className="flex justify-end space-x-2">
          <Button variant="outline" onClick={onClose}>Cancel</Button>
          <Button onClick={saveSignature}>Save Signature</Button>
        </div>
      </DialogContent>
    </Dialog>
  );
};

const CoordinatorDashboard = () => {
  const [students, setStudents] = useState([]);
  const [showSignature, setShowSignature] = useState(false);
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [actionType, setActionType] = useState('');
  const [notes, setNotes] = useState('');

  useEffect(() => {
    fetchStudents();
  }, []);

  const fetchStudents = async () => {
    try {
      const response = await axios.get(`${API}/students`);
      setStudents(response.data);
    } catch (error) {
      console.error('Error fetching students:', error);
    }
  };

  const downloadReceipt = async (studentId, tokenNumber) => {
    try {
      const response = await axios.get(`${API}/students/${studentId}/receipt`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `receipt_${tokenNumber}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading receipt:', error);
      alert('Error downloading receipt. Make sure the student is approved.');
    }
  };

  const updateStatus = async (studentId, status, notes = '', signatureData = '', signatureType = '') => {
    try {
      const formData = new FormData();
      formData.append('status', status);
      if (notes) formData.append('notes', notes);
      if (signatureData) formData.append('signature_data', signatureData);
      if (signatureType) formData.append('signature_type', signatureType);
      
      await axios.put(`${API}/students/${studentId}/status`, formData);
      fetchStudents();
    } catch (error) {
      console.error('Error updating status:', error);
    }
  };

  const handleStatusAction = (student, action) => {
    setSelectedStudent(student);
    setActionType(action);
    if (action === 'approved') {
      setShowSignature(true);
    } else {
      updateStatus(student.id, action);
    }
  };

  const handleSignatureSave = (signatureData, signatureType) => {
    if (selectedStudent) {
      updateStatus(selectedStudent.id, actionType, notes, signatureData, signatureType);
      setNotes('');
      setSelectedStudent(null);
    }
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      pending: { color: 'bg-yellow-100 text-yellow-800 border-yellow-300', icon: Clock },
      verified: { color: 'bg-blue-100 text-blue-800 border-blue-300', icon: Eye },
      approved: { color: 'bg-green-100 text-green-800 border-green-300', icon: CheckCircle },
      rejected: { color: 'bg-red-100 text-red-800 border-red-300', icon: XCircle }
    };

    const config = statusConfig[status] || statusConfig.pending;
    const IconComponent = config.icon;

    return (
      <Badge className={`${config.color} border flex items-center gap-1`}>
        <IconComponent className="h-3 w-3" />
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    );
  };

  return (
    <div className="p-6">
      <h2 className="text-2xl font-bold text-slate-800 mb-6">Coordinator Dashboard</h2>
      
      <Card>
        <CardHeader>
          <CardTitle>Student Reviews</CardTitle>
          <CardDescription>Review and approve student admissions</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Token</TableHead>
                <TableHead>Student</TableHead>
                <TableHead>Course</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Documents</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {students.map((student) => (
                <TableRow key={student.id} className={
                  student.status === 'approved' ? 'bg-green-50' :
                  student.status === 'rejected' ? 'bg-red-50' :
                  student.status === 'pending' ? 'bg-yellow-50' : ''
                }>
                  <TableCell className="font-mono">{student.token_number}</TableCell>
                  <TableCell>{student.first_name} {student.last_name}</TableCell>
                  <TableCell>{student.course}</TableCell>
                  <TableCell>{getStatusBadge(student.status)}</TableCell>
                  <TableCell>
                    <div className="flex space-x-1">
                      {Object.entries(student.documents).map(([type, path]) => (
                        <Badge key={type} variant="secondary" className="text-xs">
                          {type.replace('_', ' ').toUpperCase()}
                        </Badge>
                      ))}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex space-x-2">
                      {student.status === 'pending' && (
                        <>
                          <Button 
                            size="sm" 
                            className="bg-green-600 hover:bg-green-700 text-white"
                            onClick={() => handleStatusAction(student, 'approved')}
                          >
                            <CheckCircle className="h-4 w-4 mr-1" />
                            Approve
                          </Button>
                          <Button 
                            size="sm" 
                            className="bg-red-600 hover:bg-red-700 text-white"
                            onClick={() => handleStatusAction(student, 'rejected')}
                          >
                            <XCircle className="h-4 w-4 mr-1" />
                            Reject
                          </Button>
                        </>
                      )}
                      {student.status !== 'pending' && (
                        <div className="flex items-center space-x-2">
                          <div className="flex items-center text-sm text-gray-500">
                            {student.status === 'approved' && student.signature_data && (
                              <Badge variant="outline" className="text-green-600">
                                <Pen className="h-3 w-3 mr-1" />
                                Signed
                              </Badge>
                            )}
                            <span className="ml-2">{student.status === 'approved' ? 'Approved' : 'Processed'}</span>
                          </div>
                          {student.status === 'approved' && (
                            <Button 
                              variant="outline" 
                              size="sm"
                              onClick={() => downloadReceipt(student.id, student.token_number)}
                              title="Download Receipt"
                            >
                              <Download className="h-4 w-4" />
                            </Button>
                          )}
                        </div>
                      )}
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      <SignatureModal
        isOpen={showSignature}
        onClose={() => setShowSignature(false)}
        onSave={handleSignatureSave}
      />
    </div>
  );
};

const AdminDashboard = () => {
  const [dashboard, setDashboard] = useState(null);
  const [courseRules, setCourseRules] = useState([]);
  const [allIncentives, setAllIncentives] = useState([]);
  const [pendingUsers, setPendingUsers] = useState([]);
  const [pendingApprovals, setPendingApprovals] = useState([]);
  const [backups, setBackups] = useState([]);
  const [showCourseForm, setShowCourseForm] = useState(false);
  const [showSignatureManager, setShowSignatureManager] = useState(false);
  const [showBackupManager, setShowBackupManager] = useState(false);
  const [adminSignature, setAdminSignature] = useState(null);
  const [allStudents, setAllStudents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [editingCourse, setEditingCourse] = useState(null);
  const [courseForm, setCourseForm] = useState({ course: '', amount: '' });
  const [exportFilters, setExportFilters] = useState({
    start_date: '',
    end_date: '',
    agent_id: '',
    course: '',
    status: 'all'
  });

  useEffect(() => {
    fetchDashboard();
    fetchCourseRules();
    fetchAllIncentives();
    fetchPendingUsers();
    fetchPendingApprovals();
    fetchBackups();
    fetchAdminSignature();
    fetchAllStudents();
  }, []);

  const fetchDashboard = async () => {
    try {
      const response = await axios.get(`${API}/admin/dashboard`);
      setDashboard(response.data);
    } catch (error) {
      console.error('Error fetching dashboard:', error);
    }
  };

  const fetchCourseRules = async () => {
    try {
      const response = await axios.get(`${API}/incentive-rules`);
      setCourseRules(response.data);
    } catch (error) {
      console.error('Error fetching course rules:', error);
    }
  };

  const fetchAllIncentives = async () => {
    try {
      const response = await axios.get(`${API}/admin/incentives`);
      setAllIncentives(response.data);
    } catch (error) {
      console.error('Error fetching incentives:', error);
    }
  };

  const fetchPendingUsers = async () => {
    try {
      const response = await axios.get(`${API}/admin/pending-users`);
      setPendingUsers(response.data);
    } catch (error) {
      console.error('Error fetching pending users:', error);
    }
  };

  const fetchPendingApprovals = async () => {
    try {
      const response = await axios.get(`${API}/admin/pending-approvals`);
      setPendingApprovals(response.data);
    } catch (error) {
      console.error('Error fetching pending approvals:', error);
    }
  };

  const fetchBackups = async () => {
    try {
      const response = await axios.get(`${API}/admin/backups`);
      setBackups(response.data);
    } catch (error) {
      console.error('Error fetching backups:', error);
    }
  };

  const fetchAdminSignature = async () => {
    try {
      const response = await axios.get(`${API}/admin/signature`);
      setAdminSignature(response.data);
    } catch (error) {
      // It's okay if no signature exists
      console.log('No admin signature found');
    }
  };

  const fetchAllStudents = async () => {
    try {
      const response = await axios.get(`${API}/students`);
      setAllStudents(response.data);
    } catch (error) {
      console.error('Error fetching all students:', error);
    }
  };

  const downloadAdminReceipt = async (studentId, tokenNumber) => {
    try {
      const response = await axios.get(`${API}/admin/students/${studentId}/receipt`, {
        responseType: 'blob'
      });
      
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `admin_receipt_${tokenNumber}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading admin receipt:', error);
      alert('Error downloading receipt. Make sure the student is approved.');
    }
  };

  const handleCourseSubmit = async (e) => {
    e.preventDefault();
    try {
      const formData = new FormData();
      formData.append('course', courseForm.course);
      formData.append('amount', parseFloat(courseForm.amount));

      if (editingCourse) {
        await axios.put(`${API}/admin/courses/${editingCourse.id}`, formData);
      } else {
        await axios.post(`${API}/admin/courses`, formData);
      }
      
      setShowCourseForm(false);
      setEditingCourse(null);
      setCourseForm({ course: '', amount: '' });
      fetchCourseRules();
    } catch (error) {
      console.error('Error saving course:', error);
      alert('Error saving course. Please try again.');
    }
  };

  const deleteCourse = async (courseId) => {
    if (confirm('Are you sure you want to delete this course?')) {
      try {
        await axios.delete(`${API}/admin/courses/${courseId}`);
        fetchCourseRules();
      } catch (error) {
        console.error('Error deleting course:', error);
      }
    }
  };

  const updateIncentiveStatus = async (incentiveId, status) => {
    try {
      const formData = new FormData();
      formData.append('status', status);
      await axios.put(`${API}/admin/incentives/${incentiveId}/status`, formData);
      fetchAllIncentives();
    } catch (error) {
      console.error('Error updating incentive status:', error);
    }
  };

  const exportExcel = async () => {
    try {
      const params = new URLSearchParams();
      Object.entries(exportFilters).forEach(([key, value]) => {
        if (value && value !== 'all') params.append(key, value);
      });

      const response = await axios.get(`${API}/admin/export/excel?${params}`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'admissions_report.xlsx');
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error exporting Excel:', error);
    }
  };

  const editCourse = (course) => {
    setEditingCourse(course);
    setCourseForm({ course: course.course, amount: course.amount.toString() });
    setShowCourseForm(true);
  };

  const approveUser = async (userId) => {
    if (confirm('Are you sure you want to approve this user?')) {
      try {
        await axios.post(`${API}/admin/pending-users/${userId}/approve`);
        fetchPendingUsers();
        alert('User approved successfully');
      } catch (error) {
        console.error('Error approving user:', error);
        alert('Error approving user. Please try again.');
      }
    }
  };

  const rejectUser = async (userId) => {
    const reason = prompt('Please provide a reason for rejection:');
    if (reason !== null) {
      try {
        const formData = new FormData();
        formData.append('reason', reason);
        await axios.post(`${API}/admin/pending-users/${userId}/reject`, formData);
        fetchPendingUsers();
        alert('User rejected successfully');
      } catch (error) {
        console.error('Error rejecting user:', error);
        alert('Error rejecting user. Please try again.');
      }
    }
  };

  // New functions for 3-tier approval system
  const adminApproveStudent = async (studentId) => {
    const notes = prompt('Admin approval notes (optional):');
    if (notes !== null) {
      try {
        const formData = new FormData();
        formData.append('notes', notes || 'Approved by admin');
        await axios.put(`${API}/admin/approve-student/${studentId}`, formData);
        fetchPendingApprovals();
        fetchDashboard(); // Refresh stats
        alert('Student approved by admin successfully!');
      } catch (error) {
        console.error('Error approving student:', error);
        alert('Error approving student. Please try again.');
      }
    }
  };

  const adminRejectStudent = async (studentId) => {
    const notes = prompt('Please provide a reason for rejection:');
    if (notes) {
      try {
        const formData = new FormData();
        formData.append('notes', notes);
        await axios.put(`${API}/admin/reject-student/${studentId}`, formData);
        fetchPendingApprovals();
        alert('Student rejected by admin');
      } catch (error) {
        console.error('Error rejecting student:', error);
        alert('Error rejecting student. Please try again.');
      }
    }
  };

  // Signature management functions
  const uploadSignature = async (signatureData, signatureType) => {
    try {
      const formData = new FormData();
      formData.append('signature_data', signatureData);
      formData.append('signature_type', signatureType);
      await axios.post(`${API}/admin/signature`, formData);
      fetchAdminSignature();
      alert('Signature updated successfully!');
    } catch (error) {
      console.error('Error uploading signature:', error);
      alert('Error uploading signature. Please try again.');
    }
  };

  // Backup management functions
  const createBackup = async () => {
    try {
      setLoading(true);
      const response = await axios.post(`${API}/admin/backup`);
      alert(response.data.message);
      fetchBackups();
    } catch (error) {
      console.error('Error creating backup:', error);
      alert('Error creating backup. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 space-y-6">
      <h2 className="text-2xl font-bold text-slate-800">Admin Dashboard</h2>
      
      {/* Dashboard Stats */}
      {dashboard && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card className="border-l-4 border-blue-500">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Total Admissions</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-blue-600">{dashboard.total_admissions}</div>
            </CardContent>
          </Card>
          <Card className="border-l-4 border-green-500">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Active Agents</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-green-600">{dashboard.active_agents}</div>
            </CardContent>
          </Card>
          <Card className="border-l-4 border-yellow-500">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Incentives Paid</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-yellow-600">₹{dashboard.incentives_paid}</div>
            </CardContent>
          </Card>
          <Card className="border-l-4 border-red-500">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-gray-600">Pending Incentives</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-red-600">₹{dashboard.incentives_unpaid}</div>
            </CardContent>
          </Card>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Status Overview */}
        <Card>
          <CardHeader>
            <CardTitle>Admission Status Overview</CardTitle>
          </CardHeader>
          <CardContent>
            {dashboard && (
              <div className="space-y-4">
                <div className="flex justify-between items-center p-3 bg-yellow-50 rounded-lg border border-yellow-200">
                  <span className="font-medium text-yellow-800">Pending</span>
                  <Badge className="bg-yellow-100 text-yellow-800">{dashboard.status_breakdown.pending}</Badge>
                </div>
                <div className="flex justify-between items-center p-3 bg-green-50 rounded-lg border border-green-200">
                  <span className="font-medium text-green-800">Approved</span>
                  <Badge className="bg-green-100 text-green-800">{dashboard.status_breakdown.approved}</Badge>
                </div>
                <div className="flex justify-between items-center p-3 bg-red-50 rounded-lg border border-red-200">
                  <span className="font-medium text-red-800">Rejected</span>
                  <Badge className="bg-red-100 text-red-800">{dashboard.status_breakdown.rejected}</Badge>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Export Controls */}
        <Card>
          <CardHeader>
            <CardTitle>Data Export</CardTitle>
            <CardDescription>Generate reports with filters</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label htmlFor="start_date">Start Date</Label>
                <Input
                  id="start_date"
                  type="date"
                  value={exportFilters.start_date}
                  onChange={(e) => setExportFilters({...exportFilters, start_date: e.target.value})}
                />
              </div>
              <div>
                <Label htmlFor="end_date">End Date</Label>
                <Input
                  id="end_date"
                  type="date"
                  value={exportFilters.end_date}
                  onChange={(e) => setExportFilters({...exportFilters, end_date: e.target.value})}
                />
              </div>
            </div>
            <div>
              <Label htmlFor="filter_status">Status</Label>
              <Select value={exportFilters.status} onValueChange={(value) => setExportFilters({...exportFilters, status: value})}>
                <SelectTrigger>
                  <SelectValue placeholder="All statuses" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All statuses</SelectItem>
                  <SelectItem value="pending">Pending</SelectItem>
                  <SelectItem value="approved">Approved</SelectItem>
                  <SelectItem value="rejected">Rejected</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <Button onClick={exportExcel} className="w-full">
              <FileText className="h-4 w-4 mr-2" />
              Export Excel Report
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Course Management */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <div>
              <CardTitle>Course Management</CardTitle>
              <CardDescription>Manage courses and incentive amounts</CardDescription>
            </div>
            <Button onClick={() => setShowCourseForm(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Add Course
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Course Name</TableHead>
                <TableHead>Incentive Amount</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {courseRules.map((rule) => (
                <TableRow key={rule.id}>
                  <TableCell className="font-medium">{rule.course}</TableCell>
                  <TableCell className="text-green-600 font-medium">₹{rule.amount}</TableCell>
                  <TableCell>
                    <div className="flex space-x-2">
                      <Button size="sm" variant="outline" onClick={() => editCourse(rule)}>
                        <Edit className="h-4 w-4" />
                      </Button>
                      <Button size="sm" variant="outline" onClick={() => deleteCourse(rule.id)}>
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Incentive Management */}
      <Card>
        <CardHeader>
          <CardTitle>Incentive Management</CardTitle>
          <CardDescription>Manage agent incentive payments</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Agent</TableHead>
                <TableHead>Student</TableHead>
                <TableHead>Course</TableHead>
                <TableHead>Amount</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {allIncentives.map((incentive) => (
                <TableRow key={incentive.id}>
                  <TableCell>{incentive.agent?.username || 'N/A'}</TableCell>
                  <TableCell>{incentive.student ? `${incentive.student.first_name} ${incentive.student.last_name}` : 'N/A'}</TableCell>
                  <TableCell>{incentive.course}</TableCell>
                  <TableCell className="font-medium">₹{incentive.amount}</TableCell>
                  <TableCell>
                    <Badge className={incentive.status === 'paid' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}>
                      {incentive.status}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex space-x-2">
                      {incentive.status === 'unpaid' && (
                        <Button
                          size="sm"
                          className="bg-green-600 hover:bg-green-700"
                          onClick={() => updateIncentiveStatus(incentive.id, 'paid')}
                        >
                          Mark Paid
                        </Button>
                      )}
                      {incentive.status === 'paid' && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => updateIncentiveStatus(incentive.id, 'unpaid')}
                        >
                          Mark Unpaid
                        </Button>
                      )}
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Pending User Registrations */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Pending User Registrations</span>
            <Badge variant="outline">{pendingUsers.length} pending</Badge>
          </CardTitle>
          <CardDescription>
            Review and approve/reject new user registrations
          </CardDescription>
        </CardHeader>
        <CardContent>
          {pendingUsers.length === 0 ? (
            <div className="text-center py-6 text-gray-500">
              No pending user registrations
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Username</TableHead>
                  <TableHead>Email</TableHead>
                  <TableHead>Role</TableHead>
                  <TableHead>Agent ID</TableHead>
                  <TableHead>Submitted</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {pendingUsers.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell className="font-medium">{user.username}</TableCell>
                    <TableCell>{user.email}</TableCell>
                    <TableCell>
                      <Badge variant="outline" className="capitalize">
                        {user.role}
                      </Badge>
                    </TableCell>
                    <TableCell>{user.agent_id || 'N/A'}</TableCell>
                    <TableCell>
                      {new Date(user.created_at).toLocaleDateString()}
                    </TableCell>
                    <TableCell>
                      <div className="flex space-x-2">
                        <Button
                          size="sm"
                          variant="default"
                          className="bg-green-600 hover:bg-green-700"
                          onClick={() => approveUser(user.id)}
                        >
                          <CheckCircle className="h-4 w-4 mr-1" />
                          Approve
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          className="text-red-600 hover:bg-red-50"
                          onClick={() => rejectUser(user.id)}
                        >
                          <XCircle className="h-4 w-4 mr-1" />
                          Reject
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Admin Final Approvals (3-Tier System) */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Final Admin Approvals</span>
            <Badge variant="outline">{pendingApprovals.length} awaiting admin approval</Badge>
          </CardTitle>
          <CardDescription>
            Students approved by coordinators awaiting final admin approval (3-tier system)
          </CardDescription>
        </CardHeader>
        <CardContent>
          {pendingApprovals.length === 0 ? (
            <div className="text-center py-6 text-gray-500">
              No students awaiting admin approval
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Token</TableHead>
                  <TableHead>Student Name</TableHead>
                  <TableHead>Course</TableHead>
                  <TableHead>Agent</TableHead>
                  <TableHead>Coordinator Approved</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {pendingApprovals.map((student) => (
                  <TableRow key={student.id}>
                    <TableCell className="font-medium">{student.token_number}</TableCell>
                    <TableCell>{student.first_name} {student.last_name}</TableCell>
                    <TableCell>{student.course}</TableCell>
                    <TableCell>{student.agent?.username || 'Unknown'}</TableCell>
                    <TableCell>
                      {student.coordinator_approved_at 
                        ? new Date(student.coordinator_approved_at).toLocaleDateString()
                        : 'N/A'
                      }
                    </TableCell>
                    <TableCell>
                      <div className="flex space-x-2">
                        <Button
                          size="sm"
                          variant="default"
                          className="bg-green-600 hover:bg-green-700"
                          onClick={() => adminApproveStudent(student.id)}
                        >
                          <CheckCircle className="h-4 w-4 mr-1" />
                          Final Approve
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          className="text-red-600 hover:bg-red-50"
                          onClick={() => adminRejectStudent(student.id)}
                        >
                          <XCircle className="h-4 w-4 mr-1" />
                          Reject
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* System Management */}
      <Card>
        <CardHeader>
          <CardTitle>System Management</CardTitle>
          <CardDescription>
            Manage system settings, signatures, and backups
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            
            {/* Signature Management */}
            <div className="border rounded-lg p-4">
              <div className="flex items-center space-x-2 mb-3">
                <Pen className="h-5 w-5 text-blue-600" />
                <h3 className="font-semibold">Admin Signature</h3>
              </div>
              {adminSignature ? (
                <div className="space-y-2">
                  <div className="text-sm text-green-600 flex items-center">
                    <CheckCircle className="h-4 w-4 mr-1" />
                    Signature configured
                  </div>
                  <div className="text-xs text-gray-500">
                    Updated: {adminSignature.updated_at 
                      ? new Date(adminSignature.updated_at).toLocaleDateString() 
                      : 'Unknown'
                    }
                  </div>
                </div>
              ) : (
                <div className="text-sm text-gray-500">
                  No signature configured
                </div>
              )}
              <Button
                size="sm"
                variant="outline"
                className="w-full mt-3"
                onClick={() => setShowSignatureManager(true)}
              >
                <Upload className="h-4 w-4 mr-2" />
                Manage Signature
              </Button>
            </div>

            {/* Backup Management */}
            <div className="border rounded-lg p-4">
              <div className="flex items-center space-x-2 mb-3">
                <Archive className="h-5 w-5 text-green-600" />
                <h3 className="font-semibold">Data Backup</h3>
              </div>
              <div className="space-y-2">
                <div className="text-sm text-gray-600">
                  {backups.length} backups available
                </div>
                <div className="text-xs text-gray-500">
                  Last: {backups.length > 0 
                    ? new Date(backups[0]?.created || '').toLocaleDateString()
                    : 'Never'
                  }
                </div>
              </div>
              <div className="flex space-x-2 mt-3">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={createBackup}
                  disabled={loading}
                  className="flex-1"
                >
                  <Archive className="h-4 w-4 mr-2" />
                  {loading ? 'Creating...' : 'Backup Now'}
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => setShowBackupManager(true)}
                >
                  <Eye className="h-4 w-4" />
                </Button>
              </div>
            </div>

            {/* System Status */}
            <div className="border rounded-lg p-4">
              <div className="flex items-center space-x-2 mb-3">
                <Settings className="h-5 w-5 text-gray-600" />
                <h3 className="font-semibold">System Status</h3>
              </div>
              <div className="space-y-2">
                <div className="text-sm text-green-600 flex items-center">
                  <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                  All systems operational
                </div>
                <div className="text-xs text-gray-500">
                  3-tier approval active
                </div>
                <div className="text-xs text-gray-500">
                  Auto backup available
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Student Management - PDF Receipt Generation */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Student Management</span>
            <Badge variant="outline">{allStudents.filter(s => s.status === 'approved').length} approved students</Badge>
          </CardTitle>
          <CardDescription>
            Manage students and generate PDF receipts (Admin Console)
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="max-h-96 overflow-y-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Token #</TableHead>
                  <TableHead>Student Name</TableHead>
                  <TableHead>Course</TableHead>
                  <TableHead>Agent</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {allStudents.map((student) => (
                  <TableRow key={student.id}>
                    <TableCell className="font-medium">{student.token_number}</TableCell>
                    <TableCell>{student.first_name} {student.last_name}</TableCell>
                    <TableCell>{student.course}</TableCell>
                    <TableCell>{student.agent?.username || 'Unknown'}</TableCell>
                    <TableCell>
                      <Badge className={
                        student.status === 'approved' ? 'bg-green-100 text-green-800' :
                        student.status === 'rejected' ? 'bg-red-100 text-red-800' :
                        student.status === 'coordinator_approved' ? 'bg-blue-100 text-blue-800' :
                        'bg-yellow-100 text-yellow-800'
                      }>
                        {student.status}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex space-x-2">
                        {student.status === 'approved' && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => downloadAdminReceipt(student.id, student.token_number)}
                            title="Generate Admin PDF Receipt"
                          >
                            <Download className="h-4 w-4 mr-1" />
                            PDF Receipt
                          </Button>
                        )}
                        {student.status !== 'approved' && (
                          <span className="text-sm text-gray-400">Receipt not available</span>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
          
          {allStudents.length === 0 && (
            <div className="text-center py-6 text-gray-500">
              No students found
            </div>
          )}
        </CardContent>
      </Card>

      {/* Course Form Dialog */}
      <Dialog open={showCourseForm} onOpenChange={setShowCourseForm}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editingCourse ? 'Edit Course' : 'Add New Course'}</DialogTitle>
            <DialogDescription>
              {editingCourse ? 'Update course details' : 'Create a new course with incentive amount'}
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={handleCourseSubmit} className="space-y-4">
            <div>
              <Label htmlFor="course_name">Course Name</Label>
              <Input
                id="course_name"
                value={courseForm.course}
                onChange={(e) => setCourseForm({...courseForm, course: e.target.value})}
                placeholder="e.g., BSc Computer Science"
                required
              />
            </div>
            <div>
              <Label htmlFor="incentive_amount">Incentive Amount (₹)</Label>
              <Input
                id="incentive_amount"
                type="number"
                step="0.01"
                min="0"
                value={courseForm.amount}
                onChange={(e) => setCourseForm({...courseForm, amount: e.target.value})}
                placeholder="e.g., 5000"
                required
              />
            </div>
            <div className="flex justify-end space-x-2">
              <Button type="button" variant="outline" onClick={() => {
                setShowCourseForm(false);
                setEditingCourse(null);
                setCourseForm({ course: '', amount: '' });
              }}>
                Cancel
              </Button>
              <Button type="submit">
                {editingCourse ? 'Update Course' : 'Create Course'}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* Signature Manager Dialog */}
      <Dialog open={showSignatureManager} onOpenChange={setShowSignatureManager}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Manage Admin Signature</DialogTitle>
            <DialogDescription>
              Upload or draw your signature for official documents
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            {/* Current Signature Display */}
            {adminSignature && (
              <div className="border rounded-lg p-4">
                <Label className="text-sm font-medium">Current Signature</Label>
                <div className="mt-2 border rounded bg-gray-50 p-4">
                  <img 
                    src={adminSignature.signature_data} 
                    alt="Current signature"
                    className="max-w-full h-16 object-contain"
                  />
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  Type: {adminSignature.signature_type} | 
                  Updated: {adminSignature.updated_at 
                    ? new Date(adminSignature.updated_at).toLocaleDateString() 
                    : 'Unknown'
                  }
                </div>
              </div>
            )}

            {/* Upload New Signature */}
            <div className="space-y-3">
              <Label className="text-sm font-medium">Upload New Signature</Label>
              <input
                type="file"
                accept="image/*"
                onChange={(e) => {
                  const file = e.target.files[0];
                  if (file) {
                    const reader = new FileReader();
                    reader.onload = (event) => {
                      uploadSignature(event.target.result, 'upload');
                      setShowSignatureManager(false);
                    };
                    reader.readAsDataURL(file);
                  }
                }}
                className="block w-full text-sm text-gray-500
                  file:mr-4 file:py-2 file:px-4
                  file:rounded-full file:border-0
                  file:text-sm file:font-semibold
                  file:bg-blue-50 file:text-blue-700
                  hover:file:bg-blue-100"
              />
              
              <div className="text-center text-gray-500 text-sm">
                or
              </div>

              <Button
                variant="outline"
                className="w-full"
                onClick={() => alert('Digital signature pad feature will be added in next update')}
              >
                <Pen className="h-4 w-4 mr-2" />
                Draw Signature (Coming Soon)
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Backup Manager Dialog */}
      <Dialog open={showBackupManager} onOpenChange={setShowBackupManager}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Backup Management</DialogTitle>
            <DialogDescription>
              View and manage system backups
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <Label className="text-sm font-medium">Available Backups</Label>
              <Button 
                size="sm" 
                onClick={createBackup}
                disabled={loading}
              >
                <Plus className="h-4 w-4 mr-2" />
                {loading ? 'Creating...' : 'New Backup'}
              </Button>
            </div>

            {backups.length === 0 ? (
              <div className="text-center py-6 text-gray-500">
                No backups available
              </div>
            ) : (
              <div className="space-y-2 max-h-60 overflow-y-auto">
                {backups.map((backup, index) => (
                  <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                    <div>
                      <div className="font-medium text-sm">{backup.filename}</div>
                      <div className="text-xs text-gray-500">
                        {backup.size_mb} MB • {backup.created}
                      </div>
                    </div>
                    <div className="flex space-x-2">
                      <Button 
                        size="sm" 
                        variant="outline"
                        disabled
                        title="Restore functionality available via CLI"
                      >
                        <Download className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}

            <div className="text-xs text-gray-500 bg-blue-50 p-3 rounded">
              <strong>Note:</strong> Backup restoration should be performed by system administrators using the CLI tool located at /app/scripts/backup_system.py
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
};

const DashboardRouter = () => {
  const { user } = useAuth();

  const getDashboard = () => {
    switch (user?.role) {
      case 'agent': return <AgentDashboard />;
      case 'coordinator': return <CoordinatorDashboard />;
      case 'admin': return <AdminDashboard />;
      default: return <div>Access denied</div>;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/30 to-purple-50/30 transition-colors duration-500">
      <Header />
      
      {/* Navigation Tabs */}
      <div className="container mx-auto px-4 pt-6">
        <Tabs defaultValue="dashboard" className="w-full">
          <TabsList className="grid w-full max-w-md mx-auto grid-cols-2 mb-8 bg-white shadow-lg border border-slate-200">
            <TabsTrigger value="dashboard" className="flex items-center space-x-2">
              <Activity className="h-4 w-4" />
              <span>Dashboard</span>
            </TabsTrigger>
            <TabsTrigger value="leaderboard" className="flex items-center space-x-2">
              <Trophy className="h-4 w-4" />
              <span>Leaderboard</span>
            </TabsTrigger>
          </TabsList>
          
          <TabsContent value="dashboard">
            <main className="container mx-auto p-4">
              {getDashboard()}
            </main>
          </TabsContent>
          
          <TabsContent value="leaderboard">
            <main className="container mx-auto p-4">
              <SimpleLeaderboard />
            </main>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

const App = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<MainApp />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
};

const MainApp = () => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Loading...</div>
      </div>
    );
  }

  return user ? <DashboardRouter /> : <LoginForm />;
};

export default App;