import React from 'react';
import Hero from '../components/Hero';
import HomeNextSteps from '../components/home/HomeNextSteps';
import LocationSection from '../components/LocationSection';

export const HomePage: React.FC = () => {

  return (
    <>
      <Hero />
      <HomeNextSteps />
      <LocationSection compact />
    </>
  );
};
