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
import { Upload, Users, GraduationCap, DollarSign, FileText, Eye, CheckCircle, XCircle, Clock, Pen, Plus, Edit, Trash2, Download } from "lucide-react";
import SignatureCanvas from 'react-signature-canvas';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Auth Context
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
    <header className="bg-slate-800 text-white p-4 shadow-lg">
      <div className="container mx-auto flex justify-between items-center">
        <div className="flex items-center space-x-2">
          <GraduationCap className="h-8 w-8 text-yellow-400" />
          <h1 className="text-xl font-bold">Admission System</h1>
        </div>
        <div className="flex items-center space-x-4">
          <Badge variant="outline" className="bg-yellow-400 text-slate-800 border-yellow-400">
            {user?.role?.toUpperCase()}
          </Badge>
          <span className="hidden sm:inline">Welcome, {user?.username}</span>
          <Button variant="outline" size="sm" onClick={logout}>
            Logout
          </Button>
        </div>
      </div>
    </header>
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
                        <div className="flex items-center text-sm text-gray-500">
                          {student.status === 'approved' && student.signature_data && (
                            <Badge variant="outline" className="text-green-600">
                              <Pen className="h-3 w-3 mr-1" />
                              Signed
                            </Badge>
                          )}
                          {student.status === 'approved' ? 'Approved' : 'Processed'}
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
  const [showCourseForm, setShowCourseForm] = useState(false);
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
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main>
        {getDashboard()}
      </main>
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