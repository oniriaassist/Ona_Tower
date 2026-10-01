export const projectImages = {
  /*
   * Main Home hero and premium aerial sales visual.
   * heroOceanView remains the original Story hero background.
   */
  hero: "/ona-assets/hero/ona-home-vision-premium.png",
  heroOceanView: "/ona-assets/hero/hero-ocean-view.jpg",
  premiumAerial: "/ona-assets/hero/hero-ocean-view.jpg",

  development: {
    aerial: "/ona-assets/hero/ona-home-vision-premium.png",
    towersOverview: "/ona-assets/hero/ona-home-vision-premium.png",
    verticalFacade: "/ona-assets/architecture/tower-a-vertical.webp",
    landscape: "/ona-assets/development/landscape-gardens.webp",
    landscapePlan: "/ona-assets/development/landscape-gardens.webp",
    gardens: "/ona-assets/development/outdoor-work-garden.webp",
  },

  residences: {
    exterior: "/ona-assets/hero/ona-home-vision-premium.png",
    twoBedroomLiving: "/ona-assets/residences/2br-living.webp",
    twoBedroomPremium: "/ona-assets/residences/2br-premium-living.webp",
    threeBedroomLiving: "/ona-assets/residences/3br-living-ocean.webp",
    threeBedroomLivingWide: "/ona-assets/residences/3br-living-wide.webp",
    threeBedroomLivingTv: "/ona-assets/residences/3br-living-tv.webp",
    threeBedroomBedroom: "/ona-assets/residences/3br-bedroom.webp",
    kitchenDining: "/ona-assets/penthouses/kitchen-dining.webp",
    dining: "/ona-assets/penthouses/dining-01.webp",
    penthouseLiving: "/ona-assets/penthouses/living-01.webp",
    penthouseLivingAlt: "/ona-assets/penthouses/living-02.webp",
    penthouseDining: "/ona-assets/penthouses/dining-01.webp",
    penthouseKitchenDining: "/ona-assets/penthouses/kitchen-dining.webp",
    penthouseBedroom: "/ona-assets/penthouses/bedroom.webp",
  },

  amenities: {
    cafe: "/ona-assets/lifestyle/cafe-bakery.webp",
    socialLounge: "/ona-assets/lifestyle/social-lounge.webp",
    beautyStudio: "/ona-assets/lifestyle/beauty-studio.webp",
    miniMarket: "/ona-assets/lifestyle/mini-market.webp",
    artSalon: "/ona-assets/lifestyle/art-salon.webp",
    studyLounge: "/ona-assets/lifestyle/study-lounge.webp",
    concierge: "/ona-assets/lifestyle/concierge.webp",
    kidsClub: "/ona-assets/lifestyle/kids-club.webp",
    pool: "/ona-assets/hero/ona-home-vision-premium.png",
    gym: "/ona-assets/lifestyle/social-lounge.webp",
    coffeeCorner: "/ona-assets/lifestyle/cafe-bakery.webp",
  },

  commercial: {
    officePlan: "/ona-assets/commercial/office-workspace-premium.png",
    onaHouseExterior: "/ona-assets/commercial/ona-house-gate-premium.png",
    workspacePremium: "/ona-assets/commercial/office-workspace-premium.png",
    boardroom: "/ona-assets/commercial/office-workspace-premium.png",
    supermarket: "/ona-assets/lifestyle/mini-market.webp",
  },

  story: {
    peopleRelationships: "/ona-assets/story/people-relationships.webp",
  },

  architecture: {
    closeup: "/ona-assets/architecture/tower-a-vertical.webp",
    aerial: "/ona-assets/hero/ona-home-vision-premium.png",
  },

  floorPlans: {
    // The brochure supplies one layout per type, not per tower/orientation.
    towerA2West: "/ona-assets/cityview/floorplans/tower-a-2-ocean.jpg",
    towerA2East: "/ona-assets/cityview/floorplans/tower-a-2-ocean.jpg",
    towerA3West: "/ona-assets/floorplans/brochure-3br.png",
    towerA3East: "/ona-assets/floorplans/brochure-3br.png",
    towerAPenthouse3: "/ona-assets/floorplans/brochure-penthouse-3br.png",
    towerAPenthouse4: "/ona-assets/floorplans/brochure-penthouse-4br.png",
    towerB2West: "/ona-assets/cityview/floorplans/tower-a-2-ocean.jpg",
    towerB2East: "/ona-assets/cityview/floorplans/tower-a-2-ocean.jpg",
    towerB3West: "/ona-assets/floorplans/brochure-3br.png",
    towerB3East: "/ona-assets/floorplans/brochure-3br.png",
    towerBPenthouse3: "/ona-assets/floorplans/brochure-penthouse-3br.png",
    towerBPenthouse4: "/ona-assets/floorplans/brochure-penthouse-4br.png",
  },
} as const;

/* =========================================================
   BACKWARD-COMPATIBLE IMAGE MAP
========================================================= */

export const ONA_IMAGES = {
  heroOceanView: projectImages.heroOceanView,
  developmentAerial: projectImages.development.aerial,
  towersOverview: projectImages.development.towersOverview,
  towersVerticalFacade: projectImages.development.verticalFacade,
  outdoorLandscape: projectImages.development.landscape,
  siteLandscapePlan: projectImages.development.landscapePlan,
  landscapeGardens: projectImages.development.gardens,
  residence2BrLiving: projectImages.residences.twoBedroomLiving,
  residence3BrLiving: projectImages.residences.threeBedroomLiving,
  residence3BrBedroom: projectImages.residences.threeBedroomBedroom,
  amenityCafeBakery: projectImages.amenities.cafe,
  amenitySocialLounge: projectImages.amenities.socialLounge,
  amenityBeautyStudio: projectImages.amenities.beautyStudio,
  amenityMiniMarket: projectImages.amenities.miniMarket,
  amenityArtSalon: projectImages.amenities.artSalon,
  amenityStudyLounge: projectImages.amenities.studyLounge,
  amenityConcierge: projectImages.amenities.concierge,
  amenityKidsClub: projectImages.amenities.kidsClub,
  officeFloorPlan: projectImages.commercial.officePlan,
  architectureCloseup: projectImages.architecture.closeup,
  singleTowerAerial: projectImages.architecture.aerial,
  towerA2West: projectImages.floorPlans.towerA2West,
  towerA2East: projectImages.floorPlans.towerA2East,
  towerA3West: projectImages.floorPlans.towerA3West,
  towerA3East: projectImages.floorPlans.towerA3East,
  towerAPenthouse3: projectImages.floorPlans.towerAPenthouse3,
  towerAPenthouse4: projectImages.floorPlans.towerAPenthouse4,
  towerB2West: projectImages.floorPlans.towerB2West,
  towerB2East: projectImages.floorPlans.towerB2East,
  towerB3West: projectImages.floorPlans.towerB3West,
  towerB3East: projectImages.floorPlans.towerB3East,
  towerBPenthouse3: projectImages.floorPlans.towerBPenthouse3,
  towerBPenthouse4: projectImages.floorPlans.towerBPenthouse4,
} as const;

export type ImageKey = keyof typeof ONA_IMAGES;

export function getOnaImage(key: ImageKey): string {
  return ONA_IMAGES[key];
}

export default projectImages;
