import axios from 'axios';

const API_BASE = '/api';

export const api = {
  // Audit & Prompt
  runAudit: (userPrompt = "Go through my subscriptions and clean up anything I'm not using.") =>
    axios.post(`${API_BASE}/audit`, { user_id: "u_301", user_prompt: userPrompt }),

  sendPrompt: (prompt) =>
    axios.post(`${API_BASE}/prompt`, { user_id: "u_301", prompt }),

  resetAndSeed: () =>
    axios.post(`${API_BASE}/audit/reset-and-seed?user_id=u_301`),

  // Subscriptions
  getSubscriptions: (status = null, category = null) => {
    const params = new URLSearchParams({ user_id: 'u_301' });
    if (status) params.append('status', status);
    if (category) params.append('category', category);
    return axios.get(`${API_BASE}/subscriptions?${params.toString()}`);
  },

  addSubscription: (data) =>
    axios.post(`${API_BASE}/subscriptions`, { user_id: 'u_301', ...data }),

  performAction: (subId, action, userNote = "") =>
    axios.post(`${API_BASE}/subscriptions/${subId}/action`, { action, user_note: userNote }),

  startNegotiation: (subId) =>
    axios.post(`${API_BASE}/subscriptions/${subId}/negotiate`),

  acceptNegotiationOffer: (subId, offerId) =>
    axios.post(`${API_BASE}/subscriptions/${subId}/negotiate/${offerId}/accept`),

  declineNegotiationOffer: (subId, offerId) =>
    axios.post(`${API_BASE}/subscriptions/${subId}/negotiate/${offerId}/decline`),

  failNegotiationOffer: (subId, offerId, reason = "") =>
    axios.post(`${API_BASE}/subscriptions/${subId}/negotiate/${offerId}/fail`, null, { params: { reason } }),

  expireNegotiationOffer: (subId, offerId) =>
    axios.post(`${API_BASE}/subscriptions/${subId}/negotiate/${offerId}/expire`),

  // Guardrails
  getGuardrails: () =>
    axios.get(`${API_BASE}/guardrails?user_id=u_301`),

  updateGuardrails: (data) =>
    axios.put(`${API_BASE}/guardrails?user_id=u_301`, data),

  // Savings
  getSavings: () =>
    axios.get(`${API_BASE}/savings?user_id=u_301`),

  getSavingsReport: () =>
    axios.get(`${API_BASE}/savings/report?user_id=u_301`),

  // Audit Logs
  getAuditLogs: (limit = 50) =>
    axios.get(`${API_BASE}/audit-logs?user_id=u_301&limit=${limit}`),

  // Raw Data
  getTransactions: () =>
    axios.get(`${API_BASE}/transactions?user_id=u_301`),

  getEmails: () =>
    axios.get(`${API_BASE}/emails?user_id=u_301`),

  // Merchant Communication & Negotiation Mode
  getMerchantCommunications: (status = null, subscriptionId = null) => {
    const params = new URLSearchParams({ user_id: 'u_301' });
    if (status) params.append('status', status);
    if (subscriptionId) params.append('subscription_id', subscriptionId);
    return axios.get(`${API_BASE}/merchants/communications?${params.toString()}`);
  },

  sendMerchantNegotiation: (subscriptionId, requestType = 'DISCOUNT_REQUEST', targetDiscountPct = 25.0) =>
    axios.post(`${API_BASE}/merchants/communication/send`, {
      user_id: 'u_301',
      subscription_id: subscriptionId,
      request_type: requestType,
      target_discount_pct: targetDiscountPct
    }),

  respondMerchantNegotiation: (commId, outcome, counterPrice = null, responseText = null) =>
    axios.post(`${API_BASE}/merchants/communication/${commId}/respond`, {
      user_id: 'u_301',
      outcome,
      counter_price: counterPrice,
      response_text: responseText
    }),

  simulateTestMerchant: (subscriptionId, simulateOutcome = 'ACCEPTED', requestType = 'DISCOUNT_REQUEST') =>
    axios.post(`${API_BASE}/merchants/test-merchant/simulate`, {
      user_id: 'u_301',
      subscription_id: subscriptionId,
      simulate_outcome: simulateOutcome,
      request_type: requestType
    }),

  getPendingMerchantRequests: () =>
    axios.get(`${API_BASE}/merchants/test-merchant/pending?user_id=u_301`),
};

