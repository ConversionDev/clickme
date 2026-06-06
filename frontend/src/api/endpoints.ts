import { api, apiForm } from "./client";
import type {
  AdOut,
  AdminChatSessionOut,
  AdminUsageOut,
  AdminUserOut,
  BillingPlanOut,
  ChatMessageOut,
  ChatSessionOut,
  CreateAdminUserRequest,
  CreateChatSessionRequest,
  CreateProjectRequest,
  CreateSimulationRequest,
  CreateTextAdRequest,
  DashboardOut,
  LoginRequest,
  OrganizationOut,
  PatchAdminUserRequest,
  ProjectOut,
  ReportOut,
  SendChatMessageRequest,
  SimulationCreatedOut,
  SimulationDetailOut,
  SimulationSummaryOut,
  TokenResponse,
  UpdateProjectRequest,
  UpdateUserSettingsRequest,
  UserProfileOut,
  UserSettingsOut,
} from "./types.gen";

export const authApi = {
  login: (body: LoginRequest) => api<TokenResponse>("/api/auth/login", { method: "POST", body, auth: false }),
  logout: (refreshToken: string) =>
    api<null>("/api/auth/logout", { method: "POST", body: { refresh_token: refreshToken } }),
};

export const usersApi = {
  me: () => api<UserProfileOut>("/api/users/me"),
  settings: () => api<UserSettingsOut>("/api/users/me/settings"),
  updateSettings: (body: UpdateUserSettingsRequest) =>
    api<UserSettingsOut>("/api/users/me/settings", { method: "PATCH", body }),
  organization: (orgId: string) => api<OrganizationOut>(`/api/organizations/${orgId}`),
};

export const projectsApi = {
  list: () => api<ProjectOut[]>("/api/projects"),
  get: (id: string) => api<ProjectOut>(`/api/projects/${id}`),
  create: (body: CreateProjectRequest) => api<ProjectOut>("/api/projects", { method: "POST", body }),
  update: (id: string, body: UpdateProjectRequest) =>
    api<ProjectOut>(`/api/projects/${id}`, { method: "PATCH", body }),
  remove: (id: string) => api<null>(`/api/projects/${id}`, { method: "DELETE" }),
};

export const adsApi = {
  list: (projectId: string) => api<AdOut[]>(`/api/projects/${projectId}/ads`),
  get: (id: string) => api<AdOut>(`/api/ads/${id}`),
  createText: (body: CreateTextAdRequest) => api<AdOut>("/api/ads/text", { method: "POST", body }),
  createMultipart: (form: FormData) => apiForm<AdOut>("/api/ads", form),
};

export const simulationsApi = {
  create: (projectId: string, body: CreateSimulationRequest) =>
    api<SimulationCreatedOut>(`/api/projects/${projectId}/simulations`, { method: "POST", body }),
  list: (projectId: string) => api<SimulationSummaryOut[]>(`/api/projects/${projectId}/simulations`),
  get: (id: string) => api<SimulationDetailOut>(`/api/simulations/${id}`),
};

export const reportsApi = {
  get: (simulationId: string) => api<ReportOut>(`/api/simulations/${simulationId}/report`),
  list: () => api<ReportOut[]>("/api/reports"),
  dashboard: () => api<DashboardOut>("/api/dashboard"),
};

export const chatApi = {
  sessions: () => api<ChatSessionOut[]>("/api/chat/sessions"),
  createSession: (body: CreateChatSessionRequest) =>
    api<ChatSessionOut>("/api/chat/sessions", { method: "POST", body }),
  messages: (sessionId: string) => api<ChatMessageOut[]>(`/api/chat/sessions/${sessionId}/messages`),
  sendMessagePath: (sessionId: string) => `/api/chat/sessions/${sessionId}/messages`,
  sendMessageBody: (body: SendChatMessageRequest) => body,
};

export const adminApi = {
  users: () => api<AdminUserOut[]>("/api/admin/users"),
  createUser: (body: CreateAdminUserRequest) =>
    api<AdminUserOut>("/api/admin/users", { method: "POST", body }),
  patchUser: (id: string, body: PatchAdminUserRequest) =>
    api<AdminUserOut>(`/api/admin/users/${id}`, { method: "PATCH", body }),
  chats: () => api<AdminChatSessionOut[]>("/api/admin/chats"),
  usage: () => api<AdminUsageOut>("/api/admin/usage"),
};

export const billingApi = {
  plans: () => api<BillingPlanOut[]>("/api/billing"),
};
