import { apiRequest } from './client';

export type CityViewStatus = 'available' | 'on_hold' | 'reserved' | 'sold';

export interface CityViewUnit {
  unit_code: string;
  tower: 'Tower A' | 'Tower B' | string;
  floor_number: number | null;
  floor_label: string;
  bedrooms: number;
  residence_type: string;
  view: string;
  status: CityViewStatus;
  suite_area_sqm: number;
  balcony_area_sqm: number;
  total_area_sqm: number;
  floor_plan_url: string;
  source_page: number;
  display_order: number;
}

export interface CityViewInventory {
  units: CityViewUnit[];
  total: number;
  counts: Record<CityViewStatus, number>;
}

export function getCityViewInventory() {
  return apiRequest<CityViewInventory>('/cityview/units');
}
