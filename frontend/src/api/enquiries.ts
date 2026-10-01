import { apiRequest } from './client';

export type EnquiryType =
  | 'enquire_about_residence'
  | 'request_floor_plans'
  | 'schedule_viewing'
  | 'talk_to_sales'
  | 'general';

export interface EnquiryPayload {
  name: string;
  phone: string;
  email?: string;
  residence_interest?: string;
  enquiry_type: EnquiryType;
  message?: string;
  consent: boolean;
  source: string;
  company_website: string;
}

export interface EnquiryResponse {
  success: boolean;
  reference_number: string;
  message: string;
  customer_email_sent?: boolean;
  staff_email_sent?: boolean;
}

export async function submitEnquiry(payload: EnquiryPayload): Promise<EnquiryResponse> {
  return apiRequest<EnquiryResponse>('/enquiries', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
}
