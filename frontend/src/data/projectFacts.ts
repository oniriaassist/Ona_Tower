export const projectFacts = {
  name: "ÔNA Towers",
  company: "ONA Towers Limited",
  location: "Mazizini, Zanzibar, Tanzania",
  shortLocation: "Mazizini · Zanzibar",
  tagline: "Live above. See beyond.",

  googleEarthUrl:
    "https://earth.google.com/web/@0,-0.54754995,0a,22251752.77375655d,35y,0h,0t,0r/data=CgRCAggBQgIIAEoNCP___________wEQAA",

  locationMap: {
    latitude: -6.191499264128815,
    longitude: 39.21269416809082,
    altitude: 80,
    range: 3400,
    tilt: 58,
    heading: 325,
  },

  travelTimes: [
    {
      time: "02",
      unit: "min",
      destination: "ZNZ Airport",
    },
    {
      time: "07",
      unit: "min",
      destination: "Stone Town",
    },
    {
      time: "10",
      unit: "min",
      destination: "Ferry Port",
    },
    {
      time: "15",
      unit: "min",
      destination: "Fumba",
    },
  ],

  development: {
    towerA: {
      title: "Tower A",
      floors: "Ground + 11 residential floors + 1 penthouse level",
      typicalFloor: "4 residences per typical floor",
      mix: "2 × two-bedroom + 2 × three-bedroom",
      apartments: "46 apartments",
    },

    towerB: {
      title: "Tower B",
      floors: "Residential floors + signature penthouse level",
      typicalFloor: "4 residences per typical floor",
      mix: "Two- and three-bedroom residences",
    },

    onaHouse: {
      title: "ONA House",
      description:
        "Commercial offices, meeting spaces, everyday services and convenience within the wider ONA development.",
    },
  },
} as const;