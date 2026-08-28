import 'dart:convert';

import 'package:crypto/crypto.dart';
import 'package:flutter/material.dart';

import 'theme.dart';

const genesisPrev = '0000000000000000000000000000000000000000000000000000000000000000';

void main() {
  runApp(const TemporalLockApp());
}

class TemporalLockApp extends StatelessWidget {
  const TemporalLockApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'TemporalLock',
      debugShowCheckedModeBanner: false,
      theme: buildAppTheme(),
      home: const ChainPage(),
    );
  }
}

class Receipt {
  Receipt({
    required this.timestamp,
    required this.summary,
    required this.evidence,
    required this.confidence,
    required this.prevHash,
    required this.hash,
  });
  final String timestamp;
  final String summary;
  final String evidence;
  final double confidence;
  final String prevHash;
  final String hash;

  bool get hashOk => recompute() == hash;

  String recompute() => digest(timestamp, summary, evidence, confidence, prevHash);
}

String _conf(double c) => c.toStringAsFixed(6);

String digest(String ts, String summary, String evidence, double confidence, String prev) {
  // Canonical: sorted keys, no extra whitespace, confidence 6 decimals unquoted.
  final raw =
      '{"confidence":${_conf(confidence)},"evidence":${jsonEncode(evidence)},"prev_hash":${jsonEncode(prev)},"summary":${jsonEncode(summary)},"timestamp":${jsonEncode(ts)}}';
  return sha256.convert(utf8.encode(raw)).toString();
}

class ChainPage extends StatefulWidget {
  const ChainPage({super.key});

  @override
  State<ChainPage> createState() => _ChainPageState();
}

class _ChainPageState extends State<ChainPage> {
  final _summary = TextEditingController();
  final _evidence = TextEditingController();
  final _confidence = TextEditingController(text: '0.7');
  final _chain = <Receipt>[];
  String _verify = 'no chain yet';

  @override
  void dispose() {
    _summary.dispose();
    _evidence.dispose();
    _confidence.dispose();
    super.dispose();
  }

  String _now() => DateTime.now().toUtc().toIso8601String().split('.').first + 'Z';

  void _mint({required bool genesis}) {
    final evidence = _evidence.text;
    if (evidence.trim().isEmpty) {
      setState(() => _verify = 'empty evidence is invalid');
      return;
    }
    if (genesis && _chain.isNotEmpty) {
      setState(() => _verify = 'genesis refused: chain already exists (append only)');
      return;
    }
    if (!genesis && _chain.isEmpty) {
      setState(() => _verify = 'append refused: run genesis first');
      return;
    }
    final conf = double.tryParse(_confidence.text);
    if (conf == null || conf < 0 || conf > 1) {
      setState(() => _verify = 'confidence must be a float in [0.0, 1.0]');
      return;
    }
    final ts = _now();
    final prev = genesis ? genesisPrev : _chain.last.hash;
    final h = digest(ts, _summary.text, evidence, conf, prev);
    setState(() {
      _chain.add(Receipt(
        timestamp: ts,
        summary: _summary.text,
        evidence: evidence,
        confidence: conf,
        prevHash: prev,
        hash: h,
      ));
      _summary.clear();
      _evidence.clear();
      _verify = _runVerify();
    });
  }

  String _runVerify() {
    if (_chain.isEmpty) return 'no chain yet';
    for (var i = 0; i < _chain.length; i++) {
      final r = _chain[i];
      if (!r.hashOk) return 'BROKEN at $i: hash mismatch';
      final expectPrev = i == 0 ? genesisPrev : _chain[i - 1].hash;
      if (r.prevHash != expectPrev) return 'BROKEN at $i: prev_hash link';
    }
    return 'OK  ${_chain.length} receipt(s). Receipts, not truth claims.';
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('TemporalLock')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Text(
            'Receipts, not truth claims.',
            style: TextStyle(color: kGold, fontStyle: FontStyle.italic, fontSize: 16),
          ),
          const SizedBox(height: 8),
          const Text(
            'On-device append-only chain. A receipt is an observation note, '
            'not a verdict. Corrections are new receipts. No modify, no delete.',
          ),
          const SizedBox(height: 16),
          TextField(controller: _summary, decoration: const InputDecoration(labelText: 'Summary')),
          const SizedBox(height: 8),
          TextField(
            controller: _evidence,
            maxLines: 3,
            decoration: const InputDecoration(labelText: 'Evidence (required)', alignLabelWithHint: true),
          ),
          const SizedBox(height: 8),
          TextField(
            controller: _confidence,
            keyboardType: const TextInputType.numberWithOptions(decimal: true),
            decoration: const InputDecoration(labelText: 'Confidence [0.0, 1.0]'),
          ),
          const SizedBox(height: 12),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              FilledButton(onPressed: () => _mint(genesis: true), child: const Text('Genesis')),
              FilledButton(onPressed: () => _mint(genesis: false), child: const Text('Append')),
              OutlinedButton(
                onPressed: () => setState(() => _verify = _runVerify()),
                child: const Text('Verify'),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(_verify, style: const TextStyle(color: kGold)),
          const SizedBox(height: 16),
          for (var i = 0; i < _chain.length; i++)
            Card(
              margin: const EdgeInsets.only(bottom: 10),
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: SelectableText(
                  [
                    '#$i  ${_chain[i].timestamp}  conf=${_conf(_chain[i].confidence)}',
                    _chain[i].summary,
                    'evidence: ${_chain[i].evidence}',
                    'prev: ${_chain[i].prevHash.substring(0, 16)}…',
                    'hash: ${_chain[i].hash}',
                  ].join('\n'),
                  style: const TextStyle(fontFamily: 'monospace', fontSize: 12, height: 1.4),
                ),
              ),
            ),
        ],
      ),
    );
  }
}
