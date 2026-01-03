#!/bin/bash
echo "🧪 VALIDATION TASK-001"
echo "================================"

pytest tests/ -v --cov=src/models --cov-report=term-missing

if [ $? -eq 0 ]; then
    echo ""
    echo "================================"
    echo "✅ TASK-001 : TOUS LES TESTS PASSENT !"
    echo "================================"
    echo "🚀 Prêt pour TASK-002"
else
    echo ""
    echo "❌ Des tests ont échoué"
    exit 1
fi
