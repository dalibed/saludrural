import React, { useEffect, useState } from 'react';
import { BookOpen, Search, AlertTriangle } from 'lucide-react';
import { diccionarioService } from '../services/api';

const Diccionario = () => {
  const [terminos, setTerminos] = useState([]);
  const [filtered, setFiltered] = useState([]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadTerms = async () => {
      try {
        setLoading(true);
        const data = await diccionarioService.list();
        const list = Array.isArray(data) ? data : [];
        setTerminos(list);
        setFiltered(list);
      } catch (err) {
        console.error('Error cargando diccionario', err);
        setError('No pudimos obtener el diccionario. Intenta de nuevo más tarde.');
      } finally {
        setLoading(false);
      }
    };
    loadTerms();
  }, []);

  const handleSearch = async (value) => {
    setQuery(value);
    if (!value) {
      setFiltered(terminos);
      return;
    }
    try {
      const data = await diccionarioService.search(value);
      setFiltered(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('Error buscando término', err);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div className="card mb-10">
        <div className="flex items-center space-x-4">
          <div className="w-14 h-14 rounded-2xl bg-primary-100 text-primary-700 flex items-center justify-center">
            <BookOpen className="w-7 h-7" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-dark-800">Diccionario médico</h1>
            <p className="text-dark-500">
              Disponible sin iniciar sesión para fomentar la educación del paciente.
            </p>
          </div>
        </div>
        <div className="relative mt-6">
          <Search className="w-5 h-5 text-dark-300 absolute left-4 top-1/2 transform -translate-y-1/2" />
          <input
            className="input pl-12"
            placeholder="Busca enfermedades, tratamientos, estudios..."
            value={query}
            onChange={(e) => handleSearch(e.target.value)}
          />
        </div>
        <p className="text-xs text-dark-400 mt-2">
          Cada término explica definiciones, causas y tratamientos. Solo lectura, sin login.
        </p>
      </div>

      {loading ? (
        <div className="flex justify-center py-20">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary-200 border-t-primary-500" />
        </div>
      ) : error ? (
        <div className="p-6 rounded-2xl border border-red-100 bg-red-50 flex items-start space-x-3">
          <AlertTriangle className="w-5 h-5 text-red-500 mt-0.5" />
          <p className="text-sm text-red-600">{error}</p>
        </div>
      ) : (
        <div className="space-y-4">
          {filtered.map((termino) => (
            <article
              key={termino.ID_Diccionario || termino.id_diccionario}
              className="border border-gray-100 rounded-3xl p-6 bg-white shadow-sm hover:shadow-md transition-shadow"
            >
              <h2 className="text-xl font-semibold text-dark-700">
                {termino.Termino || termino.termino}
              </h2>
              <p className="text-sm text-dark-500 mt-2">
                <strong>Definición:</strong> {termino.Definicion || termino.definicion}
              </p>
              {termino.Causas && (
                <p className="text-sm text-dark-500 mt-2">
                  <strong>Causas:</strong> {termino.Causas}
                </p>
              )}
              {termino.Tratamientos && (
                <p className="text-sm text-dark-500 mt-2">
                  <strong>Tratamientos:</strong> {termino.Tratamientos}
                </p>
              )}
            </article>
          ))}
        </div>
      )}

      {!loading && filtered.length === 0 && (
        <p className="text-center text-dark-400 py-12">
          No encontramos términos con ese criterio de búsqueda.
        </p>
      )}
    </div>
  );
};

export default Diccionario;

