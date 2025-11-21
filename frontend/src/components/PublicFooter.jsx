import React from 'react';
import { Link } from 'react-router-dom';

const PublicFooter = () => {
  return (
    <footer className="bg-dark-900 text-white pt-12 pb-6 mt-16">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 grid grid-cols-1 md:grid-cols-4 gap-8">
        <div>
          <p className="text-2xl font-bold mb-3">Salud Rural</p>
          <p className="text-sm text-gray-300">
            Telemedicina confiable para zonas rurales de Colombia. Atención humana y tecnología
            cercana.
          </p>
        </div>
        <div>
          <p className="text-sm uppercase tracking-widest text-primary-300 mb-3">
            Plataforma
          </p>
          <ul className="space-y-2 text-sm text-gray-300">
            <li>
              <Link to="/medicos" className="hover:text-primary-200">
                Lista de médicos
              </Link>
            </li>
            <li>
              <Link to="/diccionario" className="hover:text-primary-200">
                Diccionario médico
              </Link>
            </li>
            <li>
              <Link to="/login" className="hover:text-primary-200">
                Ingresar al sistema
              </Link>
            </li>
          </ul>
        </div>
        <div>
          <p className="text-sm uppercase tracking-widest text-primary-300 mb-3">Pacientes</p>
          <ul className="space-y-2 text-sm text-gray-300">
            <li>Agendamiento en línea</li>
            <li>Videoconsultas seguras</li>
            <li>Historial clínico centralizado</li>
          </ul>
        </div>
        <div>
          <p className="text-sm uppercase tracking-widest text-primary-300 mb-3">Contacto</p>
          <ul className="space-y-2 text-sm text-gray-300">
            <li>Soporte 24/7 en WhatsApp</li>
            <li>contacto@saludrural.co</li>
            <li>+57 320 000 0000</li>
          </ul>
        </div>
      </div>
      <div className="border-t border-dark-700 mt-10 pt-4 text-center text-sm text-gray-400">
        © {new Date().getFullYear()} Salud Rural. Todos los derechos reservados.
      </div>
    </footer>
  );
};

export default PublicFooter;

