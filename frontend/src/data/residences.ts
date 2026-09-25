import {
  projectImages,
  type ImageKey,
} from "./images";

export type ResidenceVariant = {
  id: string;

  tower:
    | "Tower A"
    | "Tower B";

  orientation: string;

  suiteArea: number;

  balconyArea: number;

  totalArea: number;

  floorPlan: string;

  imageKey?: ImageKey;
};

export type ResidenceType = {
  id: string;

  label: string;

  shortLabel: string;

  bedrooms: number;

  range: string;

  description: string;

  variants: ResidenceVariant[];
};

export const residences: ResidenceType[] = [
  {
    id: "two-bedroom",

    label:
      "02 Bedroom Residence",

    shortLabel:
      "02 Bedroom",

    bedrooms: 2,

    range:
      "202–206 sqm",

    description:
      "Generous two-bedroom residences with open living spaces, private terraces and elevated views across Zanzibar.",

    variants: [
      {
        id:
          "tower-a-2-west",

        tower:
          "Tower A",

        orientation:
          "West",

        suiteArea:
          146,

        balconyArea:
          56,

        totalArea:
          202,

        floorPlan:
          projectImages
            .floorPlans
            .towerA2West,

        imageKey:
          "towerA2West",
      },

      {
        id:
          "tower-a-2-east",

        tower:
          "Tower A",

        orientation:
          "East",

        suiteArea:
          146,

        balconyArea:
          60,

        totalArea:
          206,

        floorPlan:
          projectImages
            .floorPlans
            .towerA2East,

        imageKey:
          "towerA2East",
      },

      {
        id:
          "tower-b-2-west",

        tower:
          "Tower B",

        orientation:
          "West",

        suiteArea:
          146,

        balconyArea:
          60,

        totalArea:
          206,

        floorPlan:
          projectImages
            .floorPlans
            .towerB2West,

        imageKey:
          "towerB2West",
      },

      {
        id:
          "tower-b-2-east",

        tower:
          "Tower B",

        orientation:
          "East",

        suiteArea:
          146,

        balconyArea:
          60,

        totalArea:
          206,

        floorPlan:
          projectImages
            .floorPlans
            .towerB2East,

        imageKey:
          "towerB2East",
      },
    ],
  },

  {
    id:
      "three-bedroom",

    label:
      "03 Bedroom Residence",

    shortLabel:
      "03 Bedroom",

    bedrooms:
      3,

    range:
      "236–240 sqm",

    description:
      "Expansive three-bedroom residences created around generous living, entertaining and private retreat spaces.",

    variants: [
      {
        id:
          "tower-a-3-west",

        tower:
          "Tower A",

        orientation:
          "West",

        suiteArea:
          169,

        balconyArea:
          67,

        totalArea:
          236,

        floorPlan:
          projectImages
            .floorPlans
            .towerA3West,

        imageKey:
          "towerA3West",
      },

      {
        id:
          "tower-a-3-east",

        tower:
          "Tower A",

        orientation:
          "East",

        suiteArea:
          173,

        balconyArea:
          67,

        totalArea:
          240,

        floorPlan:
          projectImages
            .floorPlans
            .towerA3East,

        imageKey:
          "towerA3East",
      },

      {
        id:
          "tower-b-3-west",

        tower:
          "Tower B",

        orientation:
          "West",

        suiteArea:
          173,

        balconyArea:
          67,

        totalArea:
          240,

        floorPlan:
          projectImages
            .floorPlans
            .towerB3West,

        imageKey:
          "towerB3West",
      },

      {
        id:
          "tower-b-3-east",

        tower:
          "Tower B",

        orientation:
          "East",

        suiteArea:
          170,

        balconyArea:
          70,

        totalArea:
          240,

        floorPlan:
          projectImages
            .floorPlans
            .towerB3East,

        imageKey:
          "towerB3East",
      },
    ],
  },

  {
    id:
      "three-bedroom-penthouse",

    label:
      "03 Bedroom Signature Penthouse",

    shortLabel:
      "03 BR Penthouse",

    bedrooms:
      3,

    range:
      "419–423 sqm",

    description:
      "A limited signature residence combining expansive living spaces, generous terraces and panoramic ocean and sunrise outlooks.",

    variants: [
      {
        id:
          "tower-a-penthouse-3",

        tower:
          "Tower A",

        orientation:
          "Supreme Ocean & Sunrise Views",

        suiteArea:
          303,

        balconyArea:
          116,

        totalArea:
          419,

        floorPlan:
          projectImages
            .floorPlans
            .towerAPenthouse3,

        imageKey:
          "towerAPenthouse3",
      },

      {
        id:
          "tower-b-penthouse-3",

        tower:
          "Tower B",

        orientation:
          "Supreme Ocean & Sunrise Views",

        suiteArea:
          303,

        balconyArea:
          120,

        totalArea:
          423,

        floorPlan:
          projectImages
            .floorPlans
            .towerBPenthouse3,

        imageKey:
          "towerBPenthouse3",
      },
    ],
  },

  {
    id:
      "four-bedroom-penthouse",

    label:
      "04 Bedroom Signature Penthouse",

    shortLabel:
      "04 BR Penthouse",

    bedrooms:
      4,

    range:
      "487–491 sqm",

    description:
      "The largest signature residences at ONA Towers, conceived for privacy, entertaining and elevated island living.",

    variants: [
      {
        id:
          "tower-a-penthouse-4",

        tower:
          "Tower A",

        orientation:
          "Supreme Ocean & Sunrise Views",

        suiteArea:
          347,

        balconyArea:
          140,

        totalArea:
          487,

        floorPlan:
          projectImages
            .floorPlans
            .towerAPenthouse4,

        imageKey:
          "towerAPenthouse4",
      },

      {
        id:
          "tower-b-penthouse-4",

        tower:
          "Tower B",

        orientation:
          "Supreme Ocean & Sunrise Views",

        suiteArea:
          357,

        balconyArea:
          134,

        totalArea:
          491,

        floorPlan:
          projectImages
            .floorPlans
            .towerBPenthouse4,

        imageKey:
          "towerBPenthouse4",
      },
    ],
  },
];

export default residences;